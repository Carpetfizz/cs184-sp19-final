const fs = require('fs');
var THREE = require('three');

getPoints();

function getPoints() {
  let rawdata = fs.readFileSync('pathPoints.json');
  let data = JSON.parse(rawdata);
  var indexPoints = data["object"]["children"].length - 1;
  var pathPoints = data["object"]["children"][indexPoints];
  var points = [];
  for (let child of pathPoints["children"]) {
    var mat = child["matrix"];
    var pos = new THREE.Vector3(mat[12], mat[13], mat[14]);
    points.push(pos);
  }
  //console.log(points);
  return points;
}
