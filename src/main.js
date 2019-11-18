var connection;
var app;
app = new Vue({
  el: '#app',
  data: {
  	query_exhibition: "",
  	artist_filter_expression: `artist.name.split(" ").some((word)=> {
	  return word == word.toLowerCase();
	});`,
	artist_filter_valid: true,
	artist_filter_error_msg: "",
  	query_gallery: "",
  	query_artist: "",
  	loaded: false,
  	load_progress: 0
  },
  computed:{
    exhibitions: function(){
    	if(this.loaded){
    		let contents = connection.exec("SELECT id, title, gallery_id, date, html FROM exhibitions WHERE title LIKE '"+"%"+this.query_exhibition+"%"+"'");
	
			if(contents.length==0)
				return []

			let items = []
			for(row of contents[0].values){
				let html =  ""+row[4];
				items.push({
					id: row[0],
					title: row[1],
					date: row[3],
					artists: getArtistsAtExhibition(connection, row[0]),
					html: html
				});
			}
			return items;
    	}else{
    		return [];
    	}
    },

    artists: function(){
    	if(this.loaded){
    		let self = this;
    		let artists = getArtists(connection, this.query_artist);
    		let expr = self.artist_filter_expression;// `artist.name.split(" ").some((word)=> { return word == word.toLowerCase(); });`
    		if(!expr)
    			return artists;

    		return artists.filter(function(artist){
    			try{
    				result = eval(expr);
    				self.artist_filter_valid = true;
    				self.artist_filter_error_msg = "";
    				return result;
    			}catch(error){
    				self.artist_filter_error_msg = error;
					self.artist_filter_valid = false;
    			}
    		});
    		
    	}
    	else{
    		return [];
    	}
    }
  }
});

var sql_select_artists_at_exhibitions = `
	SELECT a.id, a.name
	FROM artists_exhibitions ae
	INNER JOIN artists a ON a.id = ae.artist_id
	WHERE ae.exhibition_id = {};
`
function getArtistsAtExhibition(connection, exhibition_id){
	let sql = sql_select_artists_at_exhibitions.replace("{}", exhibition_id);
	console.log(sql)
	let contents = connection.exec(sql);
	let artists = [];
	for(row of contents[0].values){
		artists.push({
			id: row[0],
			name: row[1]
		});
	}
	return artists;
}

var sql_select_entities_with_filter = `
    SELECT a.id, a.name, e.id, e.title, e.date, g.id, g.name
    FROM artists_exhibitions ae
    INNER JOIN galleries g ON g.id = e.gallery_id
    INNER JOIN exhibitions e ON e.id = ae.exhibition_id
    INNER JOIN artists a ON a.id = ae.artist_id
    WHERE a.name LIKE '{a}' AND e.title LIKE '{e}' AND g.name LIKE '{g}';
    `
    
function getEntitiesTable(connection, artist_filter, gallery_filter, exhibition_filter){
	let sql = sql_select_entities_with_filter
		.replace("{a}", "%"+artist_filter+"%")
		.replace("{g}", "%"+gallery_filter+"%")
		.replace("{e}", "%"+exhibition_filter+"%");

	let contents = connection.exec(sql);
	if(contents.length==0)
		return []

	let items = {
		'artists': [],
		'galleries': [],
		'exhibitions': []
	};
	console.log(contents);
	for(row of contents[0].values){
		items['artists'].push({
			'id': row[0],
			'name': row[1]
		});

		items['exhibitions'].push({
			'id': row[2],
			'title': row[3],
			'date': row[4]
		});
		items['galleries'].push({
			'id': row[5],
			'name': row[6]
		});
		return items;
		
	}
	return items;
}

let sql_select_exhibitions = `
SELECT id, title, gallery_id, date 
FROM exhibitions 
WHERE title LIKE '%{}%'
`
function getExhibitionsTable(connection, query){
	let sql = sql_select_exhibitions.replace("{}", query);
	let contents = connection.exec();
	
	if(contents.length==0)
		return []

	let items = []
	for(row of contents[0].values){
		items.push({
			id: row[0],
			title: row[1],
			date: row[3]
		});
	}
	return items;
}

sql_select_artists = `
SELECT id, name 
FROM artists 
WHERE name LIKE '{}'
ORDER BY name ASC;
`

sql_select_artists_with_exhibition_count = `
SELECT a.id, a.name, COUNT(*)
FROM artists_exhibitions ae
INNER JOIN artists a ON a.id = ae.artist_id
GROUP BY artist_id
ORDER BY COUNT(*) DESC;
`

function getArtists(connection, query){
	let sql = sql_select_artists_with_exhibition_count.replace("{}", "%"+query+"%");
	let contents = connection.exec(sql);
	items = []
	if(contents.length==0)
		return []

	for(row of contents[0].values){
		items.push({
			id: row[0],
			name: row[1],
			exhibitioncount: row[2]
		});
	}
	return items;
}

function getGalleriesTable(connection, query){
	let contents = connection.exec("SELECT id, name FROM galleries WHERE name LIKE '"+"%"+query+"%"+"'");
	items = []
	if(contents.length==0)
		return []

	for(row of contents[0].values){
		items.push({
			id: row[0],
			name: row[1]
		});
	}
	return items;
}

function onDBLoad(database){
	connection = database;
	app.loaded=true;
	console.log("db loaded");
}

// load database
config = {
	locateFile: filename => `/vendor/${filename}` 
}

initSqlJs(config).then(function(SQL){
	var xhr = new XMLHttpRequest();
	console.log("donwload ikon.db");
	xhr.open('GET', './resources/ikon.db', true);
	xhr.responseType = 'arraybuffer';

	xhr.onprogress = function(e){
		console.log(e.total/e.loaded, "%");	
	};

	xhr.onload = function(e) {
	  var uInt8Array = new Uint8Array(this.response);
	  var connection = new SQL.Database(uInt8Array);
	  onDBLoad(connection);  
	};

	xhr.onerror = function(e) {
	  console.log("error:",e); 
	};
	xhr.send();
	var connection = new SQL.Database();
});