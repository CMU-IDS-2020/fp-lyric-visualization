import torch
from transformers import BertModel, BertTokenizer
import numpy as np
from sklearn.manifold import TSNE

# model = RobertaModel.from_pretrained('roberta-large')
model = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True)
# Initialize the tokenizer with a pretrained model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Set the device to GPU (cuda) if available, otherwise stick with CPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'

model = model.to(device)
model.eval()

def _word_embedding(word):
    """ Given a string word or words, get a numpy array representing the embedding
        return np.array[embedding_size] """
    # Code referenced from https://github.com/BramVanroy/bert-for-inference/blob/master/introduction-to-bert.ipynb
    ids = tokenizer.encode(word)
    ids = torch.LongTensor(ids).to(device)

    # unsqueeze IDs to get batch size of 1 as added dimension
    ids = ids.unsqueeze(0)

    with torch.no_grad():
        out = model(input_ids=ids)

    # we only want the hidden_states
    hidden_states = out[2]

    # get last four layers
    last_four_layers = [hidden_states[i] for i in (-1, -2, -3, -4)]
    # cast layers to a tuple and concatenate over the last dimension
    cat_hidden_states = torch.cat(tuple(last_four_layers), dim=-1)

    # take the mean of the concatenated vector over the token dimension
    cat_sentence_embedding = torch.mean(cat_hidden_states, dim=1).squeeze()
    return cat_sentence_embedding.cpu().numpy()

def word_embedding_column(col):
    """ Given a Pandas Series of words, compute the embedding for each.
        return np.array[n_words, embedding_size] """
    word_embeddings = []
    for word in col.values:
        word_embeddings.append(_word_embedding(word))
    return np.array(word_embeddings)

def tsne_column(col):
    """ Given a Pandas Series of words, compute the word embedding, then
        reduce the dimensionality with T-SNE.
        output is two np arrays for the x and y coordinates from T-SNE
        Return np.array[n_words], np.array[n_words] """
    word_embeddings = word_embedding_column(col)

    # Referecing API https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
    X = word_embeddings

    X_embedded = TSNE(n_components=2).fit_transform(X)

    return X_embedded[:,0], X_embedded[:,1]

def tsne_list(list_of_words):
    """ Given a unique list of words, compute the t-SNE coordinates.
        Return a dictionary {word: [x_value, y_value]} """
    word_embeddings = []
    for word in list_of_words:
        word_embeddings.append(_word_embedding(word))

    tsne_results = TSNE(n_components=2).fit_transform(np.array(word_embeddings))
    tsne_dict = {}
    for word in list_of_words:
        tsne_dict[word] = tsne_results[list_of_words.index(word)]
    return tsne_dict


def normalize_positivity(df):
    # Get the line positivity.
    # 1.0 if line_score is 1 and label is Positive.
    # -1.0 if linescore is 1.0 and label is Negative
    df['line_positivity'] = np.where(df['line_label'] == 'POSITIVE', df['line_score'], -1.*df['line_score'])

    # Sort, rank, then normalize to get a uniform distribution of line positivities 0-1.0
    line_positivities_sorted = sorted(df['line_positivity'].unique())
    df['line_positivity_rank'] = df['line_positivity'].apply(lambda positivity : line_positivities_sorted.index(positivity))
    df['line_positivity_norm'] = df['line_positivity_rank'] / df['line_positivity_rank'].max()

    # Get the word positivity.
    # 1.0 if hugface_score is 1 and label is Positive.
    # -1.0 if hugface_score is 1.0 and label is Negative
    df['word_positivity'] = np.where(df['hugface_label'] == 'POSITIVE', df['hugface_score'], -1.*df['hugface_score'])

    # Sort, rank, then normalize to get a uniform distribution of line positivities 0-1.0
    word_positivities_sorted = sorted(df['word_positivity'].unique())
    df['word_positivity_rank'] = df['word_positivity'].apply(lambda positivity : word_positivities_sorted.index(positivity))
    df['word_positivity_norm'] = df['word_positivity_rank'] / df['word_positivity_rank'].max()
    return df