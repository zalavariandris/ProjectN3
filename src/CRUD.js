/* HELPERS */
function loadDatabase(path, progressCallback=undefined){
    function f(SQL){
        return new Promise((resolve, reject)=>{
            const xhr = new XMLHttpRequest();
            xhr.open('GET', path, true);
            xhr.responseType = 'arraybuffer';

            if(progressCallback){
                xhr.onprogress = function(e){
                  let progress = e.loaded/e.total;
                  progressCallback(progress);
                };
            }

            xhr.onload = function(e) {
              var uInt8Array = new Uint8Array(this.response);
              let connection = new SQL.Database(uInt8Array);
              resolve(connection);
            };

            xhr.onerror = () => reject(xhr.statusText);

            xhr.send();
        });
    };
    return f;
}


export {loadDatabase};