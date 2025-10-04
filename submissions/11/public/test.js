
async function query() {
    const response = await fetch(
        "https://cloud.flowiseai.com/api/v1/prediction/eeca997d-cff7-49c8-ba49-4f080bf24eea",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        }
    );
    const result = await response.json();
    return result;
}

query().then((response) => {
    console.log(response);
    document.getElementById("result").innerHTML = "<p>" + response.text + "</p>";
});