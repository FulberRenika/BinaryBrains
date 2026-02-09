let activeCaseId = null;
let pollTimer = null;

const ORDER = [
  "Request Received",
  "Preparing",
  "Team Dispatched",
  "On the Way",
  "Action in Progress",
  "Resolved"
];

function fillSample(text){
  document.getElementById("description").value = text;
  document.getElementById("description").focus();
}

function setStepper(status){
  const steps = Array.from(document.querySelectorAll("#stepper .step"));
  const idx = ORDER.indexOf(status);

  steps.forEach((s,i)=>{
    s.classList.remove("active","done");
    if(idx === -1) return;
    if(i < idx) s.classList.add("done");
    if(i === idx) s.classList.add("active");
  });
}

async function pollStatus(){
  if(!activeCaseId) return;
  const res = await fetch(`/status/${activeCaseId}`);
  const data = await res.json();

  if(data.status){
    const statusText = document.getElementById("statusText");
    statusText.classList.remove("muted");
    statusText.textContent = data.status;
    setStepper(data.status);

    if(data.status === "Resolved" && pollTimer){
      clearInterval(pollTimer);
      pollTimer = null;
    }
  }
}

document.getElementById("reportForm").addEventListener("submit", async (e)=>{
  e.preventDefault();

  const deptPill = document.getElementById("deptPill");
  const sevPill  = document.getElementById("sevPill");
  const timePill = document.getElementById("timePill");
  const message  = document.getElementById("message");
  const statusText = document.getElementById("statusText");

  deptPill.classList.remove("muted");
  sevPill.classList.remove("muted");
  timePill.classList.remove("muted");
  message.classList.remove("muted");

  deptPill.textContent = "Departments: Analyzing...";
  sevPill.textContent  = "Severity: —";
  timePill.textContent = "Timestamp: —";
  message.textContent  = "AI is analyzing your report...";

  const form = new FormData();
  form.append("description", document.getElementById("description").value);
  const file = document.getElementById("media").files[0];
  if(file) form.append("media", file);

  const res = await fetch("/analyze", { method:"POST", body: form });
  const data = await res.json();

  activeCaseId = data.case_id;

  deptPill.textContent = `Departments: ${data.departments.join(", ")}`;
  sevPill.textContent  = `Severity: ${data.severity}`;
  timePill.textContent = `Timestamp: ${data.timestamp}`;
  message.textContent  = data.message;

  // Start status
  statusText.classList.remove("muted");
  statusText.textContent = "Request Received";
  setStepper("Request Received");

  if(pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(pollStatus, 3000);
});
