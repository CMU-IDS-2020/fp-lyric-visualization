
/** Global variable for lyrics object */
var lyrics;

/** Stopwords from the NLTK library */
var stopwords = ['i','me','my','myself','we','our','ours','ourselves','you','your','yours','yourself','yourselves','he','him','his','himself','she','her','hers','herself','it','its','itself','they','them','their','theirs','themselves','what','which','who','whom','this','that','these','those','am','is','are','was','were','be','been','being','have','has','had','having','do','does','did','doing','a','an','the','and','but','if','or','because','as','until','while','of','at','by','for','with','about','against','between','into','through','during','before','after','above','below','to','from','up','down','in','out','on','off','over','under','again','further','then','once','here','there','when','where','why','how','all','any','both','each','few','more','most','other','some','such','no','nor','not','only','own','same','so','than','too','very','s','t','can','will','just','don','should','now'];


/**
 * Get the JSON for a new song from the server
 */
function getNewSong() {
    jQuery.getJSON({
        url: '/getSong',
        type: 'GET',
        data: { artist: 'Will Smith', songName:'Just the Two of Us' }, // TODO: don't hardcode the song
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

    lyrics = data.responseJSON;

    // Sort by lyrics index
    lyrics.sort((a, b) => (a['Unnamed: 0'] > b['Unnamed: 0']) ? 1 : -1);

    // Clear the lyrics div
    jQuery('#lyrics, #scatter-plot').html('');

    buildLyricsBlock();

    // Populate the variable selects
    jQuery('#x-var-select, #y-var-select').html('');
    Object.keys(lyrics[0]).forEach(function(varName) {
        jQuery('#x-var-select, #y-var-select').append(jQuery('<option>').attr('value', varName).text(varName));
    });

    // Pre-select some variables
    jQuery('#x-var-select option[value="line_positivity_norm"]').prop('selected', true);
    jQuery('#y-var-select option[value="word_positivity_norm"]').prop('selected', true);

    buildScatterPlot();
}

function buildLyricsBlock() {
    let prevLineIndex = 0;
    let prevStanzaDescription = false;
    let lineHtml = jQuery('<div class="lyric-line" />');

    lyrics.forEach(function(lyric) {
        let lineIndex = lyric['line_index_in_song'];
        let stanzaDescription = lyric['stanza_description'];

        if (lineIndex != prevLineIndex) { // The start of a new line
            // Append the line to the lyrics section
            lineHtml.attr('line_index', lineIndex - 1);
            jQuery('#lyrics').append(lineHtml);

            // Start a new line
            lineHtml = jQuery('<div class="lyric-line" />');
            prevLineIndex = lineIndex;

            // If new line starts a new stanza, put a lil stanza description on it
            if (stanzaDescription != prevStanzaDescription) {
                // Add some space to separate stanzas
                lineHtml.append(jQuery('<div class="stanza-separator" />')
                        .text('[' + stanzaDescription + ']'));
                prevStanzaDescription = stanzaDescription;
            }

            // Add the Heat Map section. It's a right border
            let colorPercent = parseFloat(lyric['line_positivity_norm']) * 100.;
            lineHtml.css('border-left', 'solid 30px ' + perc2color(colorPercent));
        }
        let lyricSpan = lyricJsonToHtml(lyric);
        lineHtml.append(lyricSpan);
    });

    initHoverHighlightRepeatUsage();

    initHoverIsolateLyricLine();
}

/**
 * Turn a lyric JSON object into a <span>
 */
function lyricJsonToHtml(lyric) {
    return jQuery('<span />')
            .attr('id', 'lyric_' + lyric['Unnamed: 0'])
            .attr('lyricInd', lyric['Unnamed: 0'])
            .attr('line', lyric['line_index_in_song'])
            .attr('hugface_label', lyric['hugface_label'])
            .attr('word_original', lyric['word_original'])
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

/**
 * When hovering on a lyric, highlight the word used in other parts of the song
 */
function initHoverHighlightRepeatUsage() {
    jQuery('span.lyric').hover(function() {
        let thisLyricInd = parseInt(jQuery(this).attr('lyricInd'));

        // Get lyric object
        let lyricJson = lyrics[thisLyricInd];

        // Get the other instances of this word
        let otherUsesAr = JSON.parse(lyricJson['list_of_indexes']);

        otherUsesAr.forEach(function(lyricInd) {
            jQuery('span[lyricInd="' + (lyricInd-1) + '"]').addClass('same-word-highlight');
        });
    },
    function() {
        // Mouse out, remove the hover class
        jQuery('span.lyric').removeClass('same-word-highlight');
    });
}

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
        lyrics.forEach(function(lyricObj) {
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
    svg = d3.select("#scatter-plot")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");
    // Brushing code referenced from https://www.d3-graph-gallery.com/graph/interactivity_brush.html#changecss
    // Add brushing
    svg.call( d3.brush()                 // Add the brush feature using the d3.brush function
            .extent( [ [0,0], [width,height] ] ) // initialise the brush area: start at 0,0 and finishes at width,height: it means I select the whole graph area
            .on("start brush", updateChartBrushing) // Each time the brush selection changes, trigger the 'updateChartBrushing' function
        )

    // Function that is triggered when brushing is performed
    function updateChartBrushing() {
        extent = d3.event.selection
        myCircle.classed("selected-scatter-point", function(d){ return isBrushed(extent, x(d.x), y(d.y), d ) } )
    }

    // A function that return TRUE or FALSE according if a dot is in the selection or not
    // Also handles highlighting text in the lyrics block
    function isBrushed(brush_coords, cx, cy, datum) {
        var x0 = brush_coords[0][0],
        x1 = brush_coords[1][0],
        y0 = brush_coords[0][1],
        y1 = brush_coords[1][1];

        // If brushed, do stuff
        if (x0 <= cx && cx <= x1 && y0 <= cy && cy <= y1) {
            jQuery('span.lyric[word_original="' + datum.word_original + '"').addClass('selected-in-scatter-plot');
        } else {
            jQuery('span.lyric[word_original="' + datum.word_original + '"').removeClass('selected-in-scatter-plot');
        }

        return x0 <= cx && cx <= x1 && y0 <= cy && cy <= y1;    // This return TRUE or FALSE depending on if the points is in the selected area
    }

    // Function that is triggered when selecting lyrics
    function updateChartLyricSelection() {
        let selectedWords = [];
        jQuery('span.lyric.selected-lyric').each(function() { selectedWords.push(jQuery(this).attr('lyricind'));});
        myCircle.classed("selected-lyric-scatter-plot", function(d){ return isSelectedLyric(selectedWords, d ) } );
    }

    // A function that return TRUE or FALSE according to if the word is selected in the lyrics block
    function isSelectedLyric(selectedWords, datum) {
        return selectedWords.includes(String(datum.word_index_in_song-1));
    }
    // When clicking on a word in the lyrics, highlight it in the lyrics block as well as the plot
    jQuery('span.lyric').off('click');
    jQuery('span.lyric').click(function() {
        jQuery(this).hasClass('selected-lyric') ? jQuery(this).removeClass('selected-lyric') : jQuery(this).addClass('selected-lyric');
        updateChartLyricSelection();
    });

    // Get the varuables to use in the scatter plot
    let x_var = jQuery('#x-var-select option:selected').val();
    let y_var = jQuery('#y-var-select option:selected').val();

    // Get the data ready
    let data = JSON.parse(JSON.stringify(lyrics)); // Copy lyrics object
    data.forEach(function(a) { a['x'] = a[x_var]; });
    data.forEach(function(a) { a['y'] = a[y_var]; });

    // Remove stopwords
    let dataNoStopwords = [];
    data.forEach(function(a) { if (!stopwords.includes(a['word_can_search'].toLowerCase())) {dataNoStopwords.push(a);} });
    data = dataNoStopwords;

    // Add X axis
    var x = d3.scaleLinear()
        .domain(d3.extent(data, function(d) { return +d.x; }))
        .range([ 0, width ]);
    var xAxis = svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

    // Add Y axis
    var y = d3.scaleLinear()
        .domain(d3.extent(data, function(d) { return +d.y; }))
        .range([ height, 0]);
    var yAxis = svg.append("g")
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
        tooltip.html(d.word_original)
            .style("left", (d3.mouse(this)[0]+90) + "px") // It is important to put the +90: other wise the tooltip is exactly where the point is an it creates a weird effect
            .style("top", (d3.mouse(this)[1]) + "px")
    }
    // A function that change this tooltip when the leaves a point: just need to set opacity to 0 again
    var mouseleave = function(d) {
        tooltip.transition()
            .duration(200)
            .style("opacity", 0)
    }

    // Add X axis label:
    svg.append("text")
        .attr("text-anchor", "end")
        .attr("x", width/2 + margin.left)
        .attr("y", height + margin.top + 20)
        .attr('fill', '#000')
        .text('Line Positivity');//.text(x_var);
    // Y axis label:
    svg.append("text")
        .attr("text-anchor", "end")
        .attr("transform", "rotate(-90)")
        .attr("y", -margin.left + 20)
        .attr("x", -margin.top - height/2 + 20)
        .attr('fill', '#000')
        .text('Word Positivity');//.text(y_var)

    // Add dots
    var myCircle = svg.append('g')
        .selectAll("dot")
        .data(data)
        .enter()
        .append("circle")
            .attr("cx", function (d) { return x(d.x); } )
            .attr("cy", function (d) { return y(d.y); } )
            .attr("r", 5)
            .style("fill", "#69b3a280")
        .on("mouseover.tooltip", mouseover )
        .on("mousemove.tooltip", mousemove )
        .on("mouseleave.tooltip", mouseleave )
        .on('click', function(d, i) {
            if (d3.select(this).attr('class') == 'selected-scatter-point') {
                // Un select
                jQuery('span.lyric[word_original="' + d.word_original + '"').removeClass('selected-in-scatter-plot');
                d3.select(this).attr('class', '');
            } else {
                // select
                jQuery('span.lyric[word_original="' + d.word_original + '"').addClass('selected-in-scatter-plot');
                d3.select(this).attr('class', 'selected-scatter-point');
            }
        });
}
