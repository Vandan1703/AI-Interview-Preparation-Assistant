const question = document.querySelector("#question");
const button = document.querySelector("#analyze-button");
const count = document.querySelector("#char-count");
const errorMessage = document.querySelector("#error-message");
const loading = document.querySelector("#loading");
const results = document.querySelector("#results");

question.addEventListener("input", () => { count.textContent = `${question.value.length} / 6000`; });
button.addEventListener("click", analyzeQuestion);
question.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") analyzeQuestion();
});

function setText(id, value) { document.querySelector(`#${id}`).textContent = value; }
function setList(id, values) {
  const list = document.querySelector(`#${id}`);
  list.replaceChildren(...values.map((value) => { const item = document.createElement("li"); item.textContent = value; return item; }));
}
function display(analysis) {
  setText("difficulty", analysis.difficulty); setText("pattern", analysis.primary_pattern);
  setText("algorithm", analysis.algorithm_idea); setText("time-complexity", analysis.time_complexity);
  setText("space-complexity", analysis.space_complexity);
  setText("better-solution", analysis.better_solution_exists ? "Possibly" : "No material improvement");
  setText("better-notes", analysis.better_solution_notes);
  setList("hints", analysis.hints); setList("follow-ups", analysis.follow_up_questions);
  results.hidden = false; results.scrollIntoView({ behavior: "smooth", block: "start" });
}
async function analyzeQuestion() {
  const value = question.value.trim();
  errorMessage.hidden = true; results.hidden = true;
  if (value.length < 10) { errorMessage.textContent = "Please enter a fuller interview question (at least 10 characters)."; errorMessage.hidden = false; return; }
  button.disabled = true; loading.hidden = false;
  try {
    const response = await fetch("/api/analyze", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({question:value}) });
    const body = await response.json();
    if (!response.ok) throw new Error(body.detail || "The analysis could not be completed.");
    display(body.analysis);
  } catch (error) { errorMessage.textContent = error.message || "Network error. Please try again."; errorMessage.hidden = false; }
  finally { button.disabled = false; loading.hidden = true; }
}
