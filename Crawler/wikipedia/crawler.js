var bot = require('../../lib/bot'),
client = new bot('config.js'),
fs = require('fs');

var txtwiki = require('./txtwiki.js');



var helper = {
	getArticleName: function(url) {
		var output = url.slice(1,url.length);
		return decodeURIComponent(output);
	},
	getCategoriesFromArticle: function (article) {
		var categoriesTable = article.match(/\[\[Kategoria\:[\wĘęÓóĄąŚśŁłŻżŹźĆćŃń\s]+/g);
		for (var i=0; i<categoriesTable.length; i++) {
			categoriesTable[i] = categoriesTable[i].replace("[[Kategoria:", "");
		}
		return categoriesTable;



	},
	decode: function (content) {
     return decoder.write(content);
 },
 removeDuplicates: function (list) {
    list = list.sort();
    var newList = [list[0]];

    for (var i=1; i< list.length; i++) {
           if (list[i] !== newList[newList.length-1]) {
            newList.push(list[i]);
        }
    }

    return newList;
    }
}


function forBacklinks(pages) {
    var backlinks = [];
    console.log("dajesz");
    pages.forEach(function(article) {
        client.getBacklinks(article.title, function(backlinkSet) {
            for (var i=0; i<backlinkSet.length; i++) {
                if (backlinkSet[i].ns === 0) {
                    backlinks.push(backlinkSet[i].title);
                }

            }
            if (article === pages[pages.length-1]) {
                backlinks = helper.removeDuplicates(backlinks);

                backlinks.forEach(function(name) {
                    client.getArticle(name, function(content) {
                        name = name.replace(/\?/g, "");
                        fs.writeFile('/meteorica/' + name + '.txt', txtwiki.parseWikitext(content), function (err) {
                          if (err) throw err;
                          console.log('It\'s saved!');
                      });
                    });
                })

            }

        })

    });
}




client.getPagesInCategory("Zjawiska paranormalne", function (pages) {
    var pages2 = [];
    pages.forEach(function(article) {
        if (article.ns === 0){
            pages2.push(article);
        }
    });
    pages = pages2;
    pages.forEach(function(article) {
        client.getArticle(article.title, function(content) {
            fs.writeFile('/meteorica/' + article.title + '.txt', txtwiki.parseWikitext(content), function (err) {
              if (err) throw err;
              console.log('It\'s saved!');
          });
            if (article === pages[pages.length - 1]) {
                forBacklinks(pages);    
            }
        });
    });
});