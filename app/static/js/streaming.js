document.querySelector('#stop').addEventListener('click', function init() {
  document.querySelector('video').pause();
})

document.querySelector('#start').addEventListener('click', function init() {
  document.querySelector('video').play();
})

const input_video = document.getElementsByClassName('input_video')[0];
const output_canvas = document.getElementsByClassName('output_canvas')[0];
const controlElement = document.getElementsByClassName('control')[0];
const canvasCtx = output_canvas.getContext('2d');
canvas_size = Math.min(window.innerWidth, window.innerHeight);
output_canvas.width = canvas_size;
output_canvas.height = canvas_size;
const contadorElement = document.getElementsByClassName('contador')[0];
contadorElement.style.left = (canvas_size - 160) + 'px';
const fpsControl = new FPS();
const stickman_gif = document.getElementById("stickman_gif");

var current_exercise_highlight_aux;
var last_message;
const ERRORS_FRASE_LENGTH = 3; // Número máximo de frases de error a mostrar

var websocket;

window.onload = function () {

  //wesocket connection and listeners
  var loc = window.location;
  var wsStart = 'ws://';

  if (loc.protocol == 'https:') {
    wsStart = 'wss://';
  }

  var websocketURL = '/correccion/ws/' + userId + '/';

  var endPoint = wsStart + loc.host + websocketURL;

  console.log('endPoint: ', endPoint);

  websocket = new WebSocket(endPoint);

  websocket.addEventListener('open', (e) => {
    console.log('Connection Opened!');
  });
  websocket.addEventListener('message', (e) => {
    // console.log('Message received: ', e.data);
    onCorrectionReceived(e.data);
  });
  websocket.addEventListener('close', (e) => {
    console.log('Connection Closed!');
  });
  websocket.addEventListener('error', (e) => {
    console.log('Error Occured!');
  });
}

function onCorrectionReceived(data){
  //console.log("Correction received");
  last_message = JSON.parse(data);
  document.getElementById("seriesRestantes").textContent = last_message.series;
  if(last_message.Exercise_id==-1){
    document.getElementById("btn_fin_rutina").style = "display: inline";
  }
  contadorElement.innerHTML = String(last_message.count);
  if(current_exercise_highlight_aux==null){
    current_exercise_highlight_aux = last_message.Exercise_id;
    document.getElementsByClassName("ej_id_"+last_message.Exercise_id)[0].style = "background-color: #b5ff8a";
  }
  if(current_exercise_highlight_aux != last_message.Exercise_id){
    document.getElementsByClassName("ej_id_"+last_message.Exercise_id)[0].style = "background-color: #b5ff8a";
    document.getElementsByClassName("ej_id_"+current_exercise_highlight_aux)[0].style = "background-color: #fffff";
    current_exercise_highlight_aux = last_message.Exercise_id;
  }

  // Stickman gif
  switch (last_message.Exercise_id) {
    case 1:
      if(stickman_gif.getAttribute('src') != "/static/images/sentadilla_cut.gif") {stickman_gif.src = "/static/images/sentadilla_cut.gif";}
      break;
    case 2:
      if(stickman_gif.getAttribute('src') != "/static/images/zancadas_cut.gif") {stickman_gif.src = "/static/images/zancadas_cut.gif";}
      break;
    case 3:
      if(stickman_gif.getAttribute('src') != "/static/images/plancha_cut.gif") {stickman_gif.src = "/static/images/plancha_cut.gif";}
      break;
    case 4:
      if(stickman_gif.getAttribute('src') != "/static/images/biceps_curl_cut.gif") {stickman_gif.src = "/static/images/biceps_curl_cut.gif";}
      break;
    case 5:
      if(stickman_gif.getAttribute('src') != "/static/images/extension_triceps_cut.gif") {stickman_gif.src = "/static/images/extension_triceps_cut.gif";}
      break;
    case 6:
      if(stickman_gif.getAttribute('src') != "/static/images/elevaciones_frontales_cut.gif") {stickman_gif.src = "/static/images/elevaciones_frontales_cut.gif";}
      break;
    case 7:
      if(stickman_gif.getAttribute('src') != "/static/images/elevaciones_laterales_cut.gif") {stickman_gif.src = "/static/images/elevaciones_laterales_cut.gif";}
      break;
    default:
      if(stickman_gif.getAttribute('src') != "/static/images/whitegif.png") {stickman_gif.src = "/static/images/whitegif.png";}
      break;
  }

  let errorsFrase = last_message.errorsFrase ?? [];
  errorsFrase.sort();
  for(var i = 0; i < ERRORS_FRASE_LENGTH; i++){
    let errorsFrase_i = errorsFrase[i] ?? '\u00a0';
    let divElement = document.getElementsByClassName('err_txt_'+i)[0];
    if(divElement.textContent!=errorsFrase_i){
      if(!divElement.classList.contains('on_transition')){
        if(divElement.textContent == '\u00a0'){
          divElement.textContent = errorsFrase_i;
          divElement.style.opacity = "1";
          divElement.classList.add("on_transition");
        }
        else{
          divElement.style.opacity = "0";
          divElement.classList.add("on_transition");
        }
      }
    }
  }
}

document.querySelectorAll('.err_txt').forEach(item => {
  item.addEventListener('transitionend', event => {
    if(item.classList.contains("on_transition")){
      if(item.style.opacity == "0"){
        item.textContent = '\u00a0';
      }
      item.classList.remove("on_transition");
    }
  })
})



function zColor(data) {
  const z = clamp(data.from.z + 0.5, 0, 1);
  return `rgba(0, ${255 * z}, ${255 * (1 - z)}, 1)`;
}

function onResultsPose(results) {

  // results.poseLandmarks contiene todos los puntos de un frame

  try {
    if(results.poseLandmarks!=null){
      websocket.send(JSON.stringify({
        'control': 'landmarks',
        'landmarks': results.poseLandmarks
      }));
    }
  }

  catch {
  }


  if(results.poseLandmarks!=null){

  document.body.classList.add('loaded');
  fpsControl.tick();

  canvasCtx.save();
  canvasCtx.clearRect(0, 0, output_canvas.width, output_canvas.height);
  let landm_left = Object.values(POSE_LANDMARKS_RIGHT).map(index => results.poseLandmarks[index]);
  let pose_conn = POSE_CONNECTIONS.slice();
  let landm_right = Object.values(POSE_LANDMARKS_LEFT).map(index => results.poseLandmarks[index]);
  let landm_neutral = Object.values(POSE_LANDMARKS_NEUTRAL).map(index => results.poseLandmarks[index]);
  let conn_err = POSE_CONNECTIONS.slice();
  landm_left.splice(0,5);
  pose_conn.splice(0,9);
  landm_right.splice(0,5);
  landm_neutral.splice(0,1);
  canvasCtx.drawImage(
    results.image, 0, 0, output_canvas.width, output_canvas.height);
  drawConnectors(
      canvasCtx, results.poseLandmarks,pose_conn,
      {visibilityMin: 0.65, color: 'white', lineWidth: 10});
  drawLandmarks(
      canvasCtx,
      landm_right,
      {visibilityMin: 0.65, color: 'aquamarine', fillColor: 'limeGreen',lineWidth: 23});
  drawLandmarks(
      canvasCtx,
      landm_left,
      {visibilityMin: 0.65, color: 'lightSalmon', fillColor: 'chocolate', lineWidth: 23,});
  drawLandmarks(
      canvasCtx,
      landm_neutral,
      {visibilityMin: 0.65, color: 'white', fillColor: 'white', lineWidth: 23});
  drawLandmarks(
        canvasCtx,
        results.poseLandmarks.slice(0,1),
        {visibilityMin: 0.65, color: 'rgba(255, 255, 255, 0.7)', lineWidth: 23});
  drawLandmarks(canvasCtx,last_message.errors.map(x=>results.poseLandmarks[x]),
        { color: '#FF0000', lineWidth: 23 });
  drawConnectors(canvasCtx, results.poseLandmarks,pose_conn.slice().filter(n => (n.some(n2=> last_message.errors.indexOf(n2) >= 0))),
        { color: 'rgba(255,0,0,0.6)', lineWidth: 23 });


  }
  else{
    canvasCtx.drawImage(results.image, 0, 0, output_canvas.width, output_canvas.height);
  }

  canvasCtx.restore();
}

const pose = new Pose({
  locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.2/${file}`;
  }
});
pose.onResults(onResultsPose);

const camera = new Camera(input_video, {
  onFrame: async () => {
    await pose.send({ image: input_video });
  },
  width: 480,
  height: 480
});
camera.start();

new ControlPanel(controlElement, {
      selfieMode: true,
      upperBodyOnly: false,
      smoothLandmarks: true,
      minDetectionConfidence: 0.8,
      minTrackingConfidence: 0.8,
      modelComplexity: 2      
    })
    .add([fpsControl])
    .on(options => {
      input_video.classList.toggle('selfie', options.selfieMode);
      pose.setOptions(options);
    });

// Optimization: Turn off animated spinner after its hiding animation is done.
const spinner = document.querySelector(".loading");
spinner.ontransitionend = () => {
  spinner.style.display = 'none';
};

