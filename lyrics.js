
/** Global variable for lyrics object */
var lyrics0;
var lyrics1;

var lines0;
var lines1;

var positivity_barchart_data;

/** Stopwords from the NLTK library */
var stopwords = ['i','me','my','myself','we','our','ours','ourselves','you','your','yours','yourself','yourselves','he','him','his','himself','she','her','hers','herself','it','its','itself','they','them','their','theirs','themselves','what','which','who','whom','this','that','these','those','am','is','are','was','were','be','been','being','have','has','had','having','do','does','did','doing','a','an','the','and','but','if','or','because','as','until','while','of','at','by','for','with','about','against','between','into','through','during','before','after','above','below','to','from','up','down','in','out','on','off','over','under','again','further','then','once','here','there','when','where','why','how','all','any','both','each','few','more','most','other','some','such','no','nor','not','only','own','same','so','than','too','very','s','t','can','will','just','don','should','now'];


/**
 * Get the JSON for a new song from the server
 * @param isHandPickedExample - true if the queried song is one of our predefined examples.
 */
function getNewSong(isHandPickedExample) {
    jQuery('#loadingModal').modal('show');
    jQuery('#get-new-song-button').hide();

    if (!isHandPickedExample) {
        // Reset the buttons to their default look
        jQuery('.song-comparison-example button').removeClass('btn-primary').addClass('btn-outline-primary');
    }

    jQuery.getJSON({
        url: '/getSong',
        type: 'GET',
        data: {
                artist0: jQuery('input[name="artist0"]').val(),
                songName0:jQuery('input[name="song0"]').val(),
                artist1: jQuery('input[name="artist1"]').val(),
                songName1:jQuery('input[name="song1"]').val(),
                'isHandPickedExample': isHandPickedExample
        },
        complete: getNewSongCompleted
    });
}

/**
 * Received JSON for new song from server.
 * Display the lyrics and plot
 * @param data - data received from the server - lyric JSON
 */
function getNewSongCompleted(data) {
    console.log(data.responseJSON);
    jQuery('#loadingModal').modal('hide');

    lyrics0 = data.responseJSON.lyrics0;
    lyrics1 = data.responseJSON.lyrics1;
    lines0 = data.responseJSON.lines0;
    lines1 = data.responseJSON.lines1;
    positivity_barchart_data = data.responseJSON.pos_barplot_data;
    console.log(positivity_barchart_data);

    // Sort by lyrics index
    lyrics0.sort((a, b) => (a['word_index_in_song'] > b['word_index_in_song']) ? 1 : -1);
    lyrics1.sort((a, b) => (a['word_index_in_song'] > b['word_index_in_song']) ? 1 : -1);

    lines0.sort((a, b) => (a['line_index_in_song'] > b['line_index_in_song']) ? 1 : -1);
    lines1.sort((a, b) => (a['line_index_in_song'] > b['line_index_in_song']) ? 1 : -1);

    // Set variables so the plots know which song the lyrics go to
    lyrics0.forEach(function(a) { a['song_index'] = 0; });
    lyrics1.forEach(function(a) { a['song_index'] = 1; });
    lines0.forEach(function(a) { a['song_index'] = 0; });
    lines1.forEach(function(a) { a['song_index'] = 1; });

    // Clear the lyrics div
    jQuery('#lyrics0, #lyrics1, #scatter-plot, #lines-scatter-plot').html('');

    buildLyricsBlock(lyrics0, jQuery('#lyrics0'));
    buildLyricsBlock(lyrics1, jQuery('#lyrics1'));

    buildPositivityBarchart();

    // Populate the variable selects
    jQuery('#x-var-select, #y-var-select').html('');
    Object.keys(lyrics0[0]).forEach(function(varName) {
        jQuery('#x-var-select, #y-var-select').append(jQuery('<option>').attr('value', varName).text(varName));
    });
    jQuery('#x-var-lines-select, #y-var-lines-select').html('');
    Object.keys(lines0[0]).forEach(function(varName) {
        jQuery('#x-var-lines-select, #y-var-lines-select').append(jQuery('<option>').attr('value', varName).text(varName));
    });

    // Pre-select some variables
    jQuery('#x-var-select option[value="tsne_x_combined"]').prop('selected', true);
    jQuery('#y-var-select option[value="tsne_y_combined"]').prop('selected', true);


    jQuery('#x-var-lines-select option[value="tsne_x_combined"]').prop('selected', true);
    jQuery('#y-var-lines-select option[value="tsne_y_combined"]').prop('selected', true);

    buildScatterPlot();
    buildLinesScatterPlot();

    // Insert the spotify embeddings
    jQuery('#song-embedding-0').html(data.responseJSON.song0_html_embedding);
    jQuery('#song-embedding-1').html(data.responseJSON.song1_html_embedding);
}

function buildLyricsBlock(lyrics, parent) {
    let prevLineIndex = 0;
    let prevStanzaDescription = false;
    let lineHtml = jQuery('<div class="lyric-line" />');
    let lineIndex = -1;

    lyrics.forEach(function(lyric) {
        lineIndex = lyric['line_index_in_song'];
        let stanzaDescription = lyric['stanza_description'];

        if (lineIndex != prevLineIndex) { // The start of a new line
            // Append the line to the lyrics section
            lineHtml.attr('line_index', lineIndex - 1);
            parent.append(lineHtml);

            // Start a new line
            lineHtml = jQuery('<div class="lyric-line" />')
                    .attr('song_index', lyric['song_index'])
                    .attr('line_classified', lyric['line_classified']);
            prevLineIndex = lineIndex;

            // If new line starts a new stanza, put a lil stanza description on it
            if (stanzaDescription != prevStanzaDescription) {
                // Add some space to separate stanzas
                parent.append(jQuery('<div class="stanza-separator" />')
                        .text('[' + stanzaDescription + ']'));
                prevStanzaDescription = stanzaDescription;
            }

            // Add the Heat Map section. It's a right border
            // let colorPercent = parseFloat(lyric['line_positivity_norm']) * 100.;
            // lineHtml.css('border-left', 'solid 30px ' + perc2color(colorPercent));
            let color = lyric['line_label'] == 'POSITIVE' ? '#0fff01' : 'red';
            lineHtml.css('border-left', 'solid 30px ' + color);
        }
        let lyricSpan = lyricJsonToHtml(lyric);
        lineHtml.append(lyricSpan);
    });

    // Don't forget the last line :)
    lineHtml.attr('line_index', lineIndex);
    parent.append(lineHtml);

    // initHoverHighlightRepeatUsage();

    initHoverIsolateLyricLine();
}

/**
 * Turn a lyric JSON object into a <span>
 */
function lyricJsonToHtml(lyric) {
    return jQuery('<span />')
            .attr('id', 'lyric_' + lyric['word_index_in_song'])
            .attr('lyricInd', lyric['word_index_in_song'])
            .attr('song_index', lyric['song_index'])
            .attr('line', lyric['line_index_in_song'])
            .attr('hugface_label', lyric['hugface_label'])
            .attr('word_original', lyric['word_original'])
            .attr('word_can_search', lyric['word_can_search'])
            .attr('class', 'lyric')
            .text(lyric['word_original'] + ' ');
}

/**
 * Given a value 0-100, generate a color between red-to-yellow-to-green
 */
function perc2color(perc) {
    // From: https://gist.github.com/mlocati/7210513
    var r, g, b = 0;
    if(perc < 50) {
        r = 255;
        g = Math.round(5.1 * perc);
    }
    else {
        g = 255;
        r = Math.round(510 - 5.10 * perc);
    }
    var h = r * 0x10000 + g * 0x100 + b * 0x1;
    return '#' + ('000000' + h.toString(16)).slice(-6);
}

// /**
//  * When hovering on a lyric, highlight the word used in other parts of the song
//  */
// function initHoverHighlightRepeatUsage() {
//     jQuery('span.lyric').hover(function() {
//         let thisLyricInd = parseInt(jQuery(this).attr('lyricInd'));

//         // Get lyric object
//         let lyricJson = lyrics[thisLyricInd];

//         // Get the other instances of this word
//         let otherUsesAr = JSON.parse(lyricJson['list_of_indexes']);

//         otherUsesAr.forEach(function(lyricInd) {
//             jQuery('span[lyricInd="' + (lyricInd) + '"]').addClass('same-word-highlight');
//         });
//     },
//     function() {
//         // Mouse out, remove the hover class
//         jQuery('span.lyric').removeClass('same-word-highlight');
//     });
// }

/**
 * When hovering over a line of lyrics, isolate this line on the right
 * And dislay the part of speech info above each word
 */
function initHoverIsolateLyricLine() {
    jQuery('.lyric-line').hover(function() {
        let lineIndex = jQuery(this).attr('line_index');

        // Clear section
        jQuery('#lyric-line-isolation').html('');

        // Go through the lyrics JSON object and build out the line in html
        lyrics0.concat(lyrics1).forEach(function(lyricObj) {
            if (lyricObj['line_index_in_song'] == lineIndex) {
                let lyricHtml = jQuery('<span />')
                        .attr('class', 'isolated-lyric')
                        .text(lyricObj['word_original'] + ' ');
                lyricHtml.prepend(jQuery('<span />')
                        .attr('class', 'isolated-lyric-pos')
                        .text(lyricObj['broad_pos_tag']))
                jQuery('#lyric-line-isolation').append(lyricHtml);
            }
        });
    }, function() { }
    );
}

// Function that is triggered when selecting lyrics WORDS
function updateChartLyricSelection() {
    // Song 0
    let selectedWords0 = [];
    jQuery('#lyrics0 span.lyric.selected-lyric').each(function() { selectedWords0.push(jQuery(this).attr('lyricind'));});

    // Song 1
    let selectedWords1 = [];
    jQuery('#lyrics1 span.lyric.selected-lyric').each(function() { selectedWords1.push(jQuery(this).attr('lyricind'));});

    myCircle.classed("selected-lyric-scatter-plot", function(d) {
        return isSelectedLyric(selectedWords0, d, 0) || isSelectedLyric(selectedWords1, d, 1);
    });
}

// A function that return TRUE or FALSE according to if the WORD is selected in the lyrics block
function isSelectedLyric(selectedWords, datum, song_index) {
    return selectedWords.includes(String(datum.word_index_in_song)) && (datum.song_index == song_index);
}

// Clicking a word in the lyrics highlights it in the scatter plot
function clickWordInLyricsInit() {
    jQuery('span.lyric').click(function() {
        jQuery(this).hasClass('selected-lyric') ? jQuery(this).removeClass('selected-lyric') : jQuery(this).addClass('selected-lyric');
        updateChartLyricSelection();
    });
}

/**
 * Build a scatter plot
 */
function buildScatterPlot() {
    // Clear an existing plot
    jQuery('#scatter-plot').html('');

    // set the dimensions and margins of the graph
    var margin = {top: 10, right: 30, bottom: 30, left: 60},
            width = jQuery('#plots').width() - margin.left - margin.right,
            height = jQuery(window).height() - 500 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    svg_words = d3.select("#scatter-plot")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");
    // Brushing code referenced from https://www.d3-graph-gallery.com/graph/interactivity_brush.html#changecss
    // Add brushing
    wordsBrush = d3.brush()                 // Add the brush feature using the d3.brush function
            .extent( [ [0,0], [width,height] ] ) // initialise the brush area: start at 0,0 and finishes at width,height: it means I select the whole graph area
            .on("start brush", updateChartBrushing) // Each time the brush selection changes, trigger the 'updateChartBrushing' function
    svg_words.call( wordsBrush );

    // Function that is triggered when brushing is performed
    function updateChartBrushing() {
        extent = d3.event.selection
        myCircle.classed("selected-scatter-point", function(d){ return isBrushed(extent, x(d.x), y(d.y), d ) } )
    }

    // A function that return TRUE or FALSE according if a dot is in the selection or not
    // Also handles highlighting text in the lyrics block
    function isBrushed(brush_coords, cx, cy, datum) {
        if (brush_coords == null) { return false; }
        var x0 = brush_coords[0][0],
        x1 = brush_coords[1][0],
        y0 = brush_coords[0][1],
        y1 = brush_coords[1][1];

        let word_ind = String(datum.word_index_in_song);
        let song_ind = String(datum.song_index);
        let selector = 'span.lyric[lyricind="' + word_ind + '"][song_index="' + song_ind + '"]';

        // If brushed, do stuff
        if (x0 <= cx && cx <= x1 && y0 <= cy && cy <= y1) {
            jQuery(selector).addClass('selected-in-scatter-plot');
        } else {
            jQuery(selector).removeClass('selected-in-scatter-plot');
        }

        return x0 <= cx && cx <= x1 && y0 <= cy && cy <= y1;    // This return TRUE or FALSE depending on if the points is in the selected area
    }

    // Get the varuables to use in the scatter plot
    let x_var = jQuery('#x-var-select option:selected').val();
    let y_var = jQuery('#y-var-select option:selected').val();

    // Get the data ready
    let data = JSON.parse(JSON.stringify(lyrics0.concat(lyrics1))); // Copy lyrics object
    data.forEach(function(a) { a['x'] = a[x_var]; });
    data.forEach(function(a) { a['y'] = a[y_var]; });

    // // Remove stopwords
    // let dataNoStopwords = [];
    // data.forEach(function(a) { if (!stopwords.includes(a['word_can_search'].toLowerCase())) {dataNoStopwords.push(a);} });
    // data = dataNoStopwords;

    // Add X axis
    var x = d3.scaleLinear()
        .domain(d3.extent(data, function(d) { return +d.x; }))
        .range([ 0, width ]);
    var xAxis = svg_words.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

    // Add Y axis
    var y = d3.scaleLinear()
        .domain(d3.extent(data, function(d) { return +d.y; }))
        .range([ height, 0]);
    var yAxis = svg_words.append("g")
        .call(d3.axisLeft(y));

    // Add a tooltip div. Here I define the general feature of the tooltip: stuff that do not depend on the data point.
    // Its opacity is set to 0: we don't see it by default.
    var tooltip = d3.select("#scatter-plot")
        .append("div")
        .style("opacity", 0)
        .attr("class", "tooltip")
        .style("background-color", "white")
        .style("border", "solid")
        .style("border-width", "1px")
        .style("border-radius", "5px")
        .style("padding", "10px")


    // Tool tip example from https://www.d3-graph-gallery.com/graph/scatter_tooltip.html
    // A function that change this tooltip when the user hover a point.
    // Its opacity is set to 1: we can now see it. Plus it set the text and position of tooltip depending on the datapoint (d)
    var mouseover = function(d) {
        tooltip.style("opacity", 1)
    }
    var mousemove = function(d) {
        tooltip.html(d.word_can_search)
            .style("left", (d3.mouse(this)[0]+90) + "px") // It is important to put the +90: other wise the tooltip is exactly where the point is an it creates a weird effect
            .style("top", (d3.mouse(this)[1]) + "px")
    }
    // A function that change this tooltip when the leaves a point: just need to set opacity to 0 again
    var mouseleave = function(d) {
        tooltip.style("opacity", 0)
    }

    // Add X axis label:
    svg_words.append("text")
        .attr("text-anchor", "end")
        .attr("x", width/2 + margin.left)
        .attr("y", height + margin.top + 20)
        .attr('fill', '#000')
        // .text('Line Positivity');
        .text(x_var);
    // Y axis label:
    svg_words.append("text")
        .attr("text-anchor", "end")
        .attr("transform", "rotate(-90)")
        .attr("y", -margin.left + 20)
        .attr("x", -margin.top - height/2 + 20)
        .attr('fill', '#000')
        // .text('Word Positivity');
        .text(y_var);

    // Add dots
    myCircle = svg_words.append('g')
        .selectAll("dot")
        .data(data)
        .enter()
        .append("circle")
            .attr("cx", function (d) { return x(d.x); } )
            .attr("cy", function (d) { return y(d.y); } )
            .attr("r", 5)
            .style("fill", function (d) { return d.song_index == 0 ? "#69b3a280" : "#9869b380"; })
        .on("mouseover.tooltip", mouseover )
        .on("mousemove.tooltip", mousemove )
        .on("mouseleave.tooltip", mouseleave )
        .on('click', function(d, i) {
            let selector = 'span.lyric[word_can_search="' + d.word_can_search + '"]';
            if (d3.select(this).attr('class') == 'selected-scatter-point') {
                // Un select
                jQuery(selector).removeClass('selected-in-scatter-plot');
                d3.select(this).attr('class', '');
            } else {
                // select
                jQuery(selector).addClass('selected-in-scatter-plot');
                d3.select(this).attr('class', 'selected-scatter-point');
            }
        });

    // Initiallize clicking a word in the lyrics since it's a default
    clickWordInLyricsInit();
}


// Function that is triggered when selecting lines of lyrics
function updateChartLineSelection() {
    // Song 0
    let selectedLines0 = [];
    jQuery('#lyrics0 div.lyric-line.selected-lyric').each(function() { selectedLines0.push(jQuery(this).attr('line_index'));});

    // Song 1
    let selectedLines1 = [];
    jQuery('#lyrics1 div.lyric-line.selected-lyric').each(function() { selectedLines1.push(jQuery(this).attr('line_index'));});

    myCircle_lines.classed("selected-lyric-scatter-plot", function(d) {
        return isSelectedLine(selectedLines0, d, 0) || isSelectedLine(selectedLines1, d, 1);
    });
}

// A function that return TRUE or FALSE according to if the line is selected in the lyrics block
function isSelectedLine(selectedLines, datum, song_index) {
    return selectedLines.includes(String(datum.line_index_in_song)) && (datum.song_index == song_index);
}

// Clicking a LINE in the lyrics highlights it in the scatter plot
function clickLineInLyricsInit() {
    jQuery('div.lyric-line').click(function() {
        jQuery(this).hasClass('selected-lyric') ? jQuery(this).removeClass('selected-lyric') : jQuery(this).addClass('selected-lyric');
        updateChartLineSelection();
    });
}
/**
 * Build a scatter plot where each point is a line of lyrics
 */
function buildLinesScatterPlot() {
    // Clear an existing plot
    jQuery('#lines-scatter-plot').html('');

    // set the dimensions and margins of the graph
    var margin = {top: 10, right: 30, bottom: 30, left: 60},
            width = jQuery('#plots').width() - margin.left - margin.right,
            height = jQuery(window).height() - 500 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    svg_lines = d3.select("#lines-scatter-plot")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");
    // Brushing code referenced from https://www.d3-graph-gallery.com/graph/interactivity_brush.html#changecss
    // Add brushing
    linesBrush = d3.brush()                 // Add the brush feature using the d3.brush function
            .extent( [ [0,0], [width,height] ] ) // initialise the brush area: start at 0,0 and finishes at width,height: it means I select the whole graph area
            .on("start brush", updateChartBrushing) // Each time the brush selection changes, trigger the 'updateChartBrushing' function
    svg_lines.call( linesBrush )

    // Function that is triggered when brushing is performed
    function updateChartBrushing() {
        extent = d3.event.selection
        myCircle_lines.classed("selected-scatter-point", function(d){ return isBrushed(extent, x(d.x), y(d.y), d ) } )
    }

    // A function that return TRUE or FALSE according if a dot is in the selection or not
    // Also handles highlighting text in the lyrics block
    function isBrushed(brush_coords, cx, cy, datum) {
        if (brush_coords == null) { return false; }
        var x0 = brush_coords[0][0],
        x1 = brush_coords[1][0],
        y0 = brush_coords[0][1],
        y1 = brush_coords[1][1];

        let line_ind = String(datum.line_index_in_song);
        let song_ind = String(datum.song_index);
        let selector = 'div.lyric-line[line_index="' + line_ind + '"][song_index="' + song_ind + '"]';

        // If brushed, do stuff
        if (x0 <= cx && cx <= x1 && y0 <= cy && cy <= y1) {
            jQuery(selector).addClass('selected-in-scatter-plot');
        } else {
            jQuery(selector).removeClass('selected-in-scatter-plot');
        }

        return x0 <= cx && cx <= x1 && y0 <= cy && cy <= y1;    // This return TRUE or FALSE depending on if the points is in the selected area
    }

    // Get the varuables to use in the scatter plot
    let x_var = jQuery('#x-var-lines-select option:selected').val();
    let y_var = jQuery('#y-var-lines-select option:selected').val();

    // Get the data ready
    let data = JSON.parse(JSON.stringify(lines0.concat(lines1))); // Copy lyrics object
    data.forEach(function(a) { a['x'] = a[x_var]; });
    data.forEach(function(a) { a['y'] = a[y_var]; });

    // Add X axis
    var x = d3.scaleLinear()
        .domain(d3.extent(data, function(d) { return +d.x; }))
        .range([ 0, width ]);
    var xAxis = svg_lines.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

    // Add Y axis
    var y = d3.scaleLinear()
        .domain(d3.extent(data, function(d) { return +d.y; }))
        .range([ height, 0]);
    var yAxis = svg_lines.append("g")
        .call(d3.axisLeft(y));

    // Add a tooltip div. Here I define the general feature of the tooltip: stuff that do not depend on the data point.
    // Its opacity is set to 0: we don't see it by default.
    var tooltip = d3.select("#lines-scatter-plot")
        .append("div")
        .attr("class", "tooltip")
        .style("background-color", "white")
        .style("border", "solid")
        .style("border-width", "1px")
        .style("border-radius", "5px")
        .style("width", "12em")
        .style("padding", "10px")


    // Tool tip example from https://www.d3-graph-gallery.com/graph/scatter_tooltip.html
    // A function that change this tooltip when the user hover a point.
    // Its opacity is set to 1: we can now see it. Plus it set the text and position of tooltip depending on the datapoint (d)
    var mouseoverlines = function(d) {
        tooltip.style("opacity", 1)
    }
    var mousemovelines = function(d) {
        tooltip.html(d.line_original)
            .style("left", (d3.mouse(this)[0]+90) + "px") // It is important to put the +90: other wise the tooltip is exactly where the point is an it creates a weird effect
            .style("top", (d3.mouse(this)[1]) + "px")
    }
    // A function that change this tooltip when the leaves a point: just need to set opacity to 0 again
    var mouseleavelines = function(d) {
        tooltip.style("opacity", 0)
    }

    // Add X axis label:
    svg_lines.append("text")
        .attr("text-anchor", "end")
        .attr("x", width/2 + margin.left)
        .attr("y", height + margin.top + 20)
        .attr('fill', '#000')
        // .text('Line Positivity');
        .text(x_var);
    // Y axis label:
    svg_lines.append("text")
        .attr("text-anchor", "end")
        .attr("transform", "rotate(-90)")
        .attr("y", -margin.left + 20)
        .attr("x", -margin.top - height/2 + 20)
        .attr('fill', '#000')
        // .text('Word Positivity');
        .text(y_var);

    // Add dots
    myCircle_lines = svg_lines.append('g')
        .selectAll("dot")
        .data(data)
        .enter()
        .append("circle")
            .attr("cx", function (d) { return x(d.x); } )
            .attr("cy", function (d) { return y(d.y); } )
            .attr("r", 5)
            .style("fill", function (d) { return d.song_index == 0 ? "#69b3a280" : "#9869b380"; })
        .on("mouseover.tooltip", mouseoverlines )
        .on("mousemove.tooltip", mousemovelines )
        .on("mouseleave.tooltip", mouseleavelines )
        .on('click', function(d, i) {
            let selector = 'div.lyric-line[line_classified="' + d.line_classified + '"]'
            if (d3.select(this).attr('class') == 'selected-scatter-point') {
                // Un select
                jQuery(selector).removeClass('selected-in-scatter-plot');
                d3.select(this).attr('class', '');
            } else {
                // select
                jQuery(selector).addClass('selected-in-scatter-plot');
                d3.select(this).attr('class', 'selected-scatter-point');
            }
        });
}

/**
 *
 * Code adapted from https://www.d3-graph-gallery.com/graph/barplot_grouped_basicWide.html
 */
function buildPositivityBarchart() {
    // Clear an existing plot
    jQuery('#positivity-bar-chart').html('');

    // set the dimensions and margins of the graph
    var margin = {top: 10, right: 30, bottom: 30, left: 60},
        width = jQuery('#plots').width() - margin.left - margin.right,
        height = jQuery(window).height() - 500 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    var svg_pos = d3.select("#positivity-bar-chart")
        .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
        .append("g")
            .attr("transform",
                  "translate(" + margin.left + "," + margin.top + ")");


    // List of subgroups = header of the csv files = soil condition here
    var subgroups = Object.keys(positivity_barchart_data[0]);//positivity_barchart_data.columns.slice(1)
    subgroups.splice(subgroups.indexOf('group'), 1);

    // List of groups = species here = value of the first column called group -> I show them on the X axis
    var groups = positivity_barchart_data.columns;//d3.map(positivity_barchart_data, function(d){return(d.group)}).keys()

    // Add X axis
    var x = d3.scaleBand()
        .domain(groups)
            .range([0, width])
            .padding([0.2])
    svg_pos.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x).tickSize(0));

    // Add Y axis
    var y = d3.scaleLinear()
        .domain([0, 105])
        .range([ height, 0 ]);
    svg_pos.append("g")
        .call(d3.axisLeft(y));

    // Another scale for subgroup position?
    var xSubgroup = d3.scaleBand()
        .domain(subgroups)
        .range([0, x.bandwidth()])
        .padding([0.05])

    // color palette = one color per subgroup
    var color = d3.scaleOrdinal()
        .domain(subgroups)
        .range(['#69b3a280', '#9869b380'])

    // Hack to make the data object become iterable
    let iter_data = [positivity_barchart_data[0], positivity_barchart_data[1], positivity_barchart_data[2], positivity_barchart_data[3]];

    // Show the bars
    svg_pos.append("g")
        .selectAll("g")
        // Enter in data = loop group per group
        .data(iter_data)
        .enter()
        .append("g")
        .attr("transform", function(d) { return "translate(" + x(d.group) + ",0)"; })
            .selectAll("rect")
            .data(function(d) { return subgroups.map(function(key) { return {key: key, value: d[key]}; }); })
            .enter().append("rect")
        .attr("x", function(d) { return xSubgroup(d.key); })
        .attr("y", function(d) { return y(d.value); })
        .attr("width", xSubgroup.bandwidth())
        .attr("height", function(d) { return height - y(d.value); })
        .attr("fill", function(d) { return color(d.key); });
}

/**
 * Remove all selected items from the scatter plots (lyrics and lines).
 * This also means removing the selections from the lyric text itself
 */
function removeAllScatterPlotSelections() {
    // Remove selections from the scatter plots
    jQuery('#lines-scatter-plot circle, #scatter-plot circle').removeClass('selected-scatter-point');
    jQuery('#lines-scatter-plot circle, #scatter-plot circle').removeClass('selected-lyric-scatter-plot');
    // Remove selections/highlights from the text
    jQuery('.lyric-line, .lyric').removeClass('selected-in-scatter-plot');
    jQuery('.lyric-line, .lyric').removeClass('selected-lyric');

    // Remove any brushing selections.
    // Causes an exception. Can't seem to fix it. Wrapping in the try/catch works, though
    svg_lines.call(linesBrush.move, null);
    svg_words.call(wordsBrush.move, null);
}