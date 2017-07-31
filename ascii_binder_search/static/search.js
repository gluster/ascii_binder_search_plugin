$(function() {
    searchBox = $('#searchBox');
    var url = new URL(window.location.href);
    var searchText = url.searchParams.get('search-term');
    var version = url.searchParams.get('version');
    console.log(version);
    searchBox.val(searchText);
    var indexes = {};
    axios.get('versions.json')
        .then(function(response) {
            var versions = response.data['versions'];
            console.log(versions);
            var requests = [];
            var selectOptions = [];
            for (var i = 0; i < versions.length; i++) {
                console.log('data_' + versions[i]);
                requests.push(axios.get('data_' + versions[i] + '.json'))
                selectOptions.push(`<option value="${versions[i]}">${versions[i]}</option>`);
            }
            $('select').html(selectOptions);
            if (version) {
                $('select').val(version);
            }

            axios.all(requests)
                .then(function(responses) {
                    for (var i = 0; i < responses.length; i++) {
                        indexes[versions[i]] = buildIndex(responses[i].data);
                    }
                });
        })
        .catch(function(error) {
            console.log(error);
            alert("Something went wrong!");
        });

    function buildIndex(data) {
        var keys = Object.keys(data[0]);
        var index = elasticlunr(function() {
            for (var i = 0; i < keys.length; i++) {
                this.addField(keys[i]);
            }
            this.setRef("topic_url");
        });
        for (var i = 0; i < data.length; i++) {
            index.addDoc(data[i]);
        }
        return index
    }

    $('#searchBox').change(function() {
        search();
    });

    $('select').change(function() {
        search();
    });


    function search() {
        console.log("search called");
        var index = indexes[$('select').val()];
        var searchResults = index.search(searchBox.val(), {
            extend: true
        });
        var resultsMarkup = "";
        var searchResults = searchResults.splice(0, 10);
        var wordsToHighlight = [];
        var searchWords = searchBox.val().split(' ');
        for (var i = 0; i < searchWords.length; i++) {
            if (!elasticlunr.stopWordFilter.stopWords[searchWords[i]]) {
                wordsToHighlight.push(searchWords[i]);
            }
        }
        var results = [];
        for (var i = 0; i < searchResults.length; i++) {
            for (var j = 0; j < wordsToHighlight.length; j++) {
                var line = '';
                var keywordPos = searchResults[i].doc.content.toLowerCase().indexOf(wordsToHighlight[j].toLowerCase());
                if (keywordPos > -1) {
                    line += ' ' + searchResults[i].doc.content.slice(keywordPos, keywordPos + 240);
                } else {
                    line += ' ' + searchResults[i].doc.content.slice(0, 240);
                }
                line += '...';
                var re = new RegExp(wordsToHighlight[j], 'i');
                line = line.replace(re, `<b>${wordsToHighlight[j]}</b>`);
                var html = `<div class="row">
                        <a href="${searchResults[i].doc.topic_url}">${searchResults[i].doc.title}</a>
                        <span>${searchResults[i].doc.site_name + searchResults[i].doc.topic_url}</span>
                        <p>
                            ${line}
                        </p>
                    </div>`;
                //resultsMarkup += html
                results.push(html);
            }
        }
        //$('.result-wrapper').html(resultsMarkup);
        console.log(results)
        console.log(searchResults)
        $('.pagination-wrapper.row > span').html('Total Results: ' + results.length)


        $('.result-wrapper > .pagination-wrapper.row').pagination({
            dataSource: results,
            pageSize: 10,
            callback: function(data, pagination) {
                console.log(data.length);
                var container = $('.result-wrapper > .results');
                container.html('');
                for (var i = 0; i < data.length; i++) {
                    container.append(data[i]);
                }
            }
        });
    }
});