
fetch('data/motion.json')
.then((response) => {
    return response.json();
})
.then((motion) => {
    fetch('data/scene.json')
    .then((response) => {
        return response.json();
    })
    .then((scene) => {
        // console.log(scene);
        init(motion, scene);
    })
}).catch(function (error) {
    console.log(error);
});

const ROLL_KEY = "Roll(rads)"
const PITCH_KEY = "Pitch(rads)"
const YAW_KEY = "Yaw(rads)"

function lerp(v0, v1, t) {
    return (1 - t) * v0 + t * v1;
}

function getValues(dict, k) {
    values = []
    for (let i = 0; i < Object.keys(dict['Timestamp']).length; i++) {
        values.push(dict[k][String(i)])
    }
    return values;
}

function setupScene(sceneData) {

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    
    // OBJECT
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshLambertMaterial({ color: 0x00ff00 });
    const cube = new THREE.Mesh(geometry, material );
    cube.position.y = 0.5;
    scene.add(cube);
    
    // GROUND
    const groundGeo = new THREE.PlaneGeometry(400,400);
    const groundTexture = new THREE.TextureLoader().load('textures/grass.jpg');
    groundTexture.wrapS = groundTexture.wrapT = THREE.RepeatWrapping;
    groundTexture.offset.set( 0, 0 );
    groundTexture.repeat.set(20, 20);
    const groundMat = new THREE.MeshBasicMaterial({map: groundTexture});
    const ground = new THREE.Mesh(groundGeo,groundMat); 
    ground.position.y = 0; //lower it 
    ground.rotation.x = -Math.PI/2; //-90 degrees around the xaxis 
    ground.doubleSided = true; 
    scene.add(ground);

    // SKYBOX
    // const skyGeo = new THREE.CubeGeometry(1000, 1000, 1000, 1, 1, 1, null, true);
    // const urls = [
    //     'skybox/hills_rt.png',
    //     'skybox/hills_lf.png',
    //     'skybox/hills_up.png',
    //     'skybox/hills_dn.png',
    //     'skybox/hills_bk.png',
    //     'skybox/hills_ft.png'
    // ]
	
	// var skyMats = [];
	// for (var i = 0; i < 6; i++)
	// 	skyMats.push( new THREE.MeshBasicMaterial({
	// 		map: new THREE.TextureLoader().load(urls[i]),
	// 		side: THREE.BackSide
	// 	}));
	// var skybox = new THREE.Mesh(skyGeo, skyMats);
    // scene.add( skybox );
    
    // LIGHTING

    var light = new THREE.HemisphereLight( 0x87ceeb, 0x008000, 1 );
    scene.add( light );

    return scene;
}

function setupCurve(scene, positions) {
    var curve = new THREE.CatmullRomCurve3(positions);

    const points = curve.getPoints( 50 );
    const curveGeo = new THREE.BufferGeometry().setFromPoints( points );
    const curveMat = new THREE.LineBasicMaterial( { color : 0xff0000 } );
    
    // Create the final object to add to the scene
    const curveObject = new THREE.Line( curveGeo, curveMat );
    scene.add(curveObject);
    return curve;
}

function init(motion, sceneData) {
    const scene = setupScene(sceneData);
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000 );
    const points  = [
        new THREE.Vector3(0, 0.01, 30),
        new THREE.Vector3(0, 5, 20),
        new THREE.Vector3( 0, 0.5, 1)
    ]
    const curve = setupCurve(scene, points);

    const renderer = new THREE.WebGLRenderer();
    renderer.setSize( window.innerWidth, window.innerHeight );
    document.body.appendChild( renderer.domElement );

    rolls = getValues(motion, ROLL_KEY);
    pitches = getValues(motion, PITCH_KEY);
    yaws = getValues(motion, YAW_KEY);

    let t = 0;
    let damping = 0.1;

    let duration =  6 * 1000; // ms
    let start = Date.now();

    function animate() {
        requestAnimationFrame( animate );
        let roll, pitch, yaw;
        let f = (Date.now() - start) / duration;

        // add some linear interpolation ?
        if (f <= 1) {
            let pos = curve.getPointAt(f);
            camera.position.copy(pos);
        }

        const j = t % 5;

        if (j == 0) {
            roll = rolls[t];
            pitch = pitches[t];
            yaw = yaws[t];
        } else {
            const s = (j/6 - (j-1)/5) / (1/5);
            roll = lerp(rolls[t-1], rolls[t], s);
            pitch = lerp(pitches[t-1], pitches[t], s);
            yaw = lerp(yaws[t-1], yaws[t], s);
        }

        if (t < rolls.length) {
            camera.rotation.x = pitch * damping;
            camera.rotation.y = roll * damping;
            camera.rotation.z = yaw * damping;
        } else {
            t = 0;
        }
        renderer.render( scene, camera );
        t += 1;
    }
    animate();
}