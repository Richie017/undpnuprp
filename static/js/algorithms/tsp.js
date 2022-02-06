/**
 * Created by shamilsakib on 4/21/2016.
 */

var NUM_POINTS = 10;
var gCities;
var gStrands;
var POPULATION_SIZE = 1000;

var gWorkers = [];
var NUM_WORKERS = 10;

var gInc = POPULATION_SIZE / NUM_WORKERS;
var gNumComplete = 0;
var gNumIterations = 10;
var gCurrentIteration = 0;


var MainLoop = function () {
    $('input:button').attr('disabled', 'true');
    gNumIterations = $('#numIterations').val();
    $('#status').append('Beginning ' + gNumIterations + ' generations...');
    gCurrentIteration = 0;
    Evolve();
}

var InitCities = function () {
    NUM_CITIES = $('#numCities').val();
    gCities = [];

    for (var i = 0; i < NUM_CITIES; i++) {
        gCities[i] = {x: rInt(gWidth), y: rInt(gHeight)};
    }
};

var InitCanvas = function () {
    gCanvasInput = $("#canvasInput")[0];

    var w = gWidth;
    var h = gHeight;

    gCanvasInput.style.width = w + "px";
    gCanvasInput.style.height = h + "px";
    gCanvasInput.width = w;
    gCanvasInput.height = h;

    gCtxInput = gCanvasInput.getContext("2d");
}

var rInt = function (limit) {
    return Math.floor(Math.random() * limit);
};

var rFloat = function (limit) {
    return Math.random() * limit;
};

var CopyArray = function (from, to) {
    for (var i = 0; i < from.length; i++) {
        to[i] = from[i];
    }
};

var Evolve = function () {

    // Breed from the top-two results we have
    var breedFrom = 5;

    for (var i = breedFrom; i < gStrands.length - (breedFrom - 1); i++) {
        for (var j = 0; j < breedFrom; j++) {
            CopyArray(gStrands[j].dna, gStrands[i + j].dna);
        }
    }

    gNumComplete = 0;
    gCurrentIteration++;

    // Loop through all the workers and given them something to do
    for (var i = 0; i < gWorkers.length; i++) {

        var tmpArray = [];

        for (var j = 0; j < gInc; j++) {
            tmpArray[j] = gStrands[j + (i * gInc)];
        }

        gWorkers[i].postMessage({
            workerId: i,
            msg: "run",
            data: tmpArray
        });
    }

};

var InitDNA = function () {

    var dna = [];

    for (var i = 0; i < NUM_CITIES; i++) {
        var city = -1;
        // loop until we find a city that has not already been chosen
        do {
            city = rInt(NUM_CITIES);
        } while ($.inArray(city, dna) !== -1);
        dna[i] = city;
    }
    return dna;
};

var dist = function (sx, sy, dx, dy) {
    return Math.sqrt(((sx - dx) * (sx - dx)) + ((sy - dy) * (sy - dy)));
};

var getDistance = function (p1, p2) {
    return dist(p1.x, p1.y, p2.x, p2.y);
};

var TestFitness = function (dna) {
    var fit = 0;
    for (var i = 1; i < dna.length; i++) {
        fit += getDistance(gCities[dna[i - 1]], gCities[dna[i]]);
    }
    return Math.round(fit);
};

var ScorePopulation = function () {
    $(gStrands).each(function (i, value) {
        value.score = TestFitness(value.dna);
    });

    // sort by fitness
    gStrands.sort(function (a, b) {
        return a.score - b.score;
    });
};

// Initializes the Population
var InitStrands = function () {
    gStrands = [];
    for (var i = 0; i < POPULATION_SIZE; i++) {
        gStrands[i] = {dna: [], score: Number.MAX_VALUE};
        gStrands[i].dna = InitDNA();
    }
    ScorePopulation();
    $('#fit').html("Initial fit is " + gStrands[0].score);
};

var Draw = function (ctx, dna) {
    ctx.clearRect(0, 0, gWidth, gHeight);
    ctx.fillStyle = "rgb(100,100,255)";

    // draw all the cities
    $(gCities).each(function (index, value) {
        ctx.beginPath();
        ctx.arc(value.x, value.y, 6, 0, Math.PI * 2, true);
        ctx.closePath();
        ctx.fill();
    });

    // draw the route
    ctx.beginPath();
    ctx.moveTo(gCities[dna[0]].x, gCities[dna[0]].y);

    $(dna).each(function (index, value) {
        ctx.lineTo(gCities[value].x, gCities[value].y);
    });

    ctx.closePath();
    ctx.stroke();

    return;
};

function supports_web_workers() {
    return !!window.Worker;
}

var InitWorkers = function () {
    for (var i = 0; i < NUM_WORKERS; i++) {
        gWorkers[i].postMessage({msg: "init", data: gCities});
    }
};

var Init = function () {
    InitCities();
    InitStrands();
};

$(document).ready(function () {

    InitCanvas();
    Init();

    if (supports_web_workers) {
        $('#fit').append("<br/>Workers are supported<br/>");
    } else {
        $('#fit').append("<br/>Sorry, HTML Workers are NOT supported. Try this demo in Firefox or Opera instead<br/>");
        return;
    }

    //Declare a worker
    for (var i = 0; i < NUM_WORKERS; i++) {
        gWorkers[i] = new Worker('worker.js');

        //Process message received FROM the worker
        gWorkers[i].onmessage = function (event) {
            // was this ack generated as part of initialization?
            if (event.data.msg === "init") {
                return;
            }
            if (event.data.msg === "done") {

                var obj = event.data;
                //$('#status').append('workerId = ' + obj.workerId + ' done = ' + gNumComplete + "<br/>");

                for (var i = 0; i < obj.data.length; i++) {
                    gStrands[(obj.workerId * gInc) + i].dna = obj.data[i].dna;
                    gStrands[(obj.workerId * gInc) + i].score = obj.data[i].score;
                }

                gNumComplete++;

                // Have all workers completed?
                if (gNumComplete < gWorkers.length) {
                    // no, let's give this guy more work.
                } else {
                    // all work was done
                    // sort by fitness
                    gStrands.sort(function (a, b) {
                        return a.score - b.score;
                    });
                    Draw(gCtxInput, gStrands[0].dna);
                    //$('#fit').append(gStrands[0].score +"<br/>");
                    if (gCurrentIteration < gNumIterations) {
                        Evolve();
                    } else {
                        $('#status').append(gStrands[0].score + "");
                        $('input:button').removeAttr('disabled');
                        $('#status').append('...done!<br/>');

                    }
                }
            }
        }
    }

    InitWorkers();
    MainLoop();

    return;
});
