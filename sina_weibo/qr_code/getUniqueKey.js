const getUniqueKey = function () {
    var b = (new Date).getTime().toString();
    var c = 1;
    return b + c++
    // return b
}

console.log(getUniqueKey());