document.addEventListener('touchmove', function (event) {
  if (event.scale !== 1) { event.preventDefault(); }
}, { passive: false });

var renderer;
var camera;
var controls;
var scene;
var sun;
function init(){
    /*
     * Setup threejs scene
     */
    renderer = new THREE.WebGLRenderer({antialias: false, depth: true, alpha: false});
    // renderer.setClearColor("black", 1.0)
    renderer.setSize( window.innerWidth, window.innerHeight );
    renderer.shadowMap.enabled = false;
    renderer.shadowMap.type = THREE.BasicShadowMap;
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(renderer.getClearColor(), 0.75)

    camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.0001, 10 );
    camera.position.z = 1;


    sun = new THREE.DirectionalLight();
    sun.position.set(1,1,0);
    sun.castShadow = true;
    scene.add(sun);

    element = document.body
    element = document.getElementById("graph")
    element.appendChild( renderer.domElement );

    controls = new THREE.TrackballControls( camera, renderer.domElement );
    controls.update();
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.07;
}

class GraphObject{
    constructor(G){
        this.graph_obj = new THREE.Object3D();
        this.G = G
        this.create_links()
        this.create_labels()
    }

    create_links(){
        let nodes = this.G['nodes'];
        let edges = this.G['edges'];

        let geometry = new THREE.BufferGeometry();
        let vertices = new Float32Array( edges.length*(3+3) );
        let colors = new Uint8Array(vertices.length/3.0*3.0 );

        for(let e=0; e<edges.length; e++){
            let edge = edges[e];
            let s = nodes[edge['source']];
            let t = nodes[edge['target']];

            vertices[e*6+0] = s['pos'][0];
            vertices[e*6+1] = s['pos'][1];
            vertices[e*6+2] = s['pos'][2];

            vertices[e*6+3+0] = t['pos'][0];
            vertices[e*6+3+1] = t['pos'][1];
            vertices[e*6+3+2] = t['pos'][2];

            // Color edges by direction
            let r = Math.abs(s['pos'][0] - t['pos'][0]);
            let g = Math.abs(s['pos'][1] - t['pos'][1]);
            let b = Math.abs(s['pos'][2] - t['pos'][2]);
            let length = Math.sqrt(r*r+g*g+b*b);
            r/=length;
            g/=length;
            b/=length;
            colors[e*6+0] = colors[e*6+3+0] = r*255;
            colors[e*6+1] = colors[e*6+3+1] = b*255;
            colors[e*6+2] = colors[e*6+3+2] = g*255;
        }
        geometry.addAttribute( 'position', new THREE.BufferAttribute( vertices, 3 ) );
        geometry.addAttribute( 'color', new THREE.BufferAttribute( colors, 3, true ) );

        // links
        let web_material = new THREE.LineBasicMaterial( {
            transparent: true,
            opacity: 0.5,
            color: "white",
            vertexColors: THREE.VertexColors,
            //blending: THREE.AdditiveBlending
        } );
        let web = new THREE.LineSegments( geometry, web_material );
        web.renderOrder = -1;
        this.graph_obj.add( web );
    }

    create_labels(){
        let nodes = this.G.nodes;
        let labels = new THREE.Group()
        for(let n in nodes)
        {
            // attributes
            let text = nodes[n].label;
            let textHeight = 0.0015;
            let fontFace = "Futura";
            let fontSize = 32;
            let font = "normal "+fontSize+"px"+" "+fontFace;

            // create canvas
            let canvas = document.createElement('canvas');
            let ctx = canvas.getContext("2d");
            ctx.font = font;
            let textWidth = ctx.measureText(text).width;
            canvas.width = textWidth;
            canvas.height = fontSize;

            ctx.font = font;
            ctx.textAlign = "left";
            ctx.textBaseline = 'bottom';
            if(canvas.width>0 && canvas.height>0){
                // ctx.fillStyle = "blue";
                // ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "white";
                ctx.fillText(text, 0, canvas.height);

                // create texture
                let tex = new THREE.Texture(canvas);
                tex.needsUpdate = true;
                let spriteMat = new THREE.SpriteMaterial({
                    map: tex,
                    sizeAttenuation: true,
                    premultipliedAlpha: false
                });
                let sprite = new THREE.Sprite(spriteMat);
                let o = new THREE.Object3D()
                o.add(sprite);

                sprite.position.set(nodes[n]['pos'][0], nodes[n]['pos'][1], nodes[n]['pos'][2]);
                let aspect = canvas.width/canvas.height;
                sprite.center = new THREE.Vector2(1,0);
                sprite.scale.set(textHeight * aspect, textHeight);
                labels.add(sprite);
            }else{
                console.log(text, textWidth, fontSize);
            }
            this.graph_obj.add(labels);
        }
    }

    create_dots(){
            
            let nodes = this.G['nodes'];
            let geometry = new THREE.BufferGeometry();
            let vertices = new Float32Array(Object.keys(nodes).length*3);
            let colors = new Uint8Array(Object.keys(nodes).length*3);

            for(let n in nodes){
                let i = nodes[n]['idx'];
                let pos = nodes[n]['pos'];
                vertices[i*3+0] = pos[0];
                vertices[i*3+1] = pos[1];
                vertices[i*3+2] = pos[2];

                let color = new THREE.Color(nodes[n]['color']);
                colors[i*3+0] = color.r*255;
                colors[i*3+1] = color.g*255;
                colors[i*3+2] = color.b*255;
            }
            //geometry.addAttribute( 'position', new THREE.BufferAttribute( vertices, 3 ) );
            //geometry.addAttribute( 'color', new THREE.BufferAttribute( colors, 3, true ) );


            let dots_material = new THREE.PointsMaterial( { 
              color: 0x888888,
                sizeAttenuation: true,
                size: 0.001,
                color: "white",
                vertexColors: THREE.VertexColors
            } );
            let dots = new THREE.Points( geometry, dots_material );
            graph_obj.add(dots);
    }

    create_spheres(){
        let spheres_obj = new THREE.Group();
        let nodes = G['nodes'];

        let geomety = new THREE.IcosahedronBufferGeometry(0.0003, 0);


        for(let n in nodes){
            let material = new THREE.MeshToonMaterial({
                color: nodes[n]['color'],
                wireframe: false
            });

            let mesh = new THREE.Mesh(geomety, material);        
            mesh.position.set(nodes[n]['pos'][0], nodes[n]['pos'][1], nodes[n]['pos'][2])
            mesh.scale.set(nodes[n]['size'], nodes[n]['size'], nodes[n]['size'])
            spheres_obj.add(mesh);
        }
        graph_obj.add(spheres_obj);
    }

    create_tubes(){
        let nodes = G['nodes'];
        let edges = G['edges'];
        let geometry = new THREE.CylinderBufferGeometry(0.00005, 0.00005, 1, 3, 1);
        geometry.translate(0,0.5,0);
        geometry.rotateX(Math.PI/2);

        let tubes = new THREE.Group();
        for(let e=0; e<edges.length; e++){
            let edge = edges[e];
            let s = nodes[edge['source']];
            let t = nodes[edge['target']];


            let s_vec = new THREE.Vector3(s.pos[0], s.pos[2], s.pos[2]);
            let t_vec = new THREE.Vector3(t.pos[0], t.pos[2], t.pos[2]);

            let distance = s_vec.distanceTo(t_vec);
            let material = new THREE.MeshToonMaterial({
                color: "white"
            });
            let tube = new THREE.Mesh(geometry, material);
            tube.scale.set(1, 1, distance);

            tube.position.set(s.pos[0], s.pos[1], s.pos[2]);
            tube.lookAt(t.pos[0], t.pos[1], t.pos[2] );
            tube.receiveShadow = true;
            tube.castShadow = true;
            tubes.add(tube);
        }

        graph_obj.add(tubes);
    }
}

/* =======
   HELPERS
   =======*/
function goto(name){
    //search
    let node;
    for(let n in nodes){
        if(nodes[n].label == name){
            node = n; 
        }
    }
    if(node==undefined){
        return false;
    }

    pos = nodes[node].pos;
    camera.position.set(pos[0], pos[1], pos[2]-0.015);
    controls.update();
    controls.target.set(pos[0], pos[1], pos[2]);
    controls.update();
    return true;
}


/* ======
 * INIT
   ======*/
   // stats
var stats = new Stats();
stats.showPanel( 0 ); // 0: fps, 1: ms, 2: mb, 3+: custom
stats.dom.style.left = '';
stats.dom.style.right = '0px';
stats.dom.style.top = '0px';
document.body.appendChild( stats.dom );

init()



fetch("./resources/ikon_artists_exhibitions_graph.json")
.then((resp)=> resp.json())
.then(function(G){
    graphObject = new GraphObject(G)
    scene.add(graphObject.graph_obj);
});

window.addEventListener( 'resize', onWindowResize, false );
function onWindowResize(){
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight );
}

/* ======
 * RENDER
   ======*/
function animate() {
    requestAnimationFrame( animate );

    stats.begin();
    controls.update();
    scene.updateMatrixWorld();
    scene.traverse( function ( object ) {
        if ( object instanceof THREE.LOD ) {
            object.update( camera );
        }
    } );
    renderer.render( scene, camera );
    stats.end();
}
animate();



