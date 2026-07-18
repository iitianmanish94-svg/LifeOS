document.querySelectorAll('[data-habit]').forEach((el) => el.addEventListener('click', async () => {
  const response = await fetch(`/api/habits/${el.dataset.habit}/toggle`, {method: 'POST', headers: {'X-CSRFToken': CSRF_TOKEN}});
  if (!response.ok) return;
  const data = await response.json();
  const card = el.closest('.habit-card, .habit-row');
  if (card) card.classList.toggle('done', data.completed);
  document.querySelectorAll('.ring').forEach(r => {r.style.setProperty('--progress', data.percent); r.querySelector('b').textContent=`${data.percent}%`;});
}));
const clock=document.getElementById('clock'); if(clock){const tick=()=>{const parts=new Intl.DateTimeFormat('en-IN',{hour:'numeric',minute:'2-digit',hour12:true,timeZone:'Asia/Kolkata'}).formatToParts(new Date());const hour=Number(parts.find(part=>part.type==='hour').value);const period=parts.find(part=>part.type==='dayPeriod').value;clock.textContent=parts.map(part=>part.value).join('');const greeting=document.getElementById('greeting');if(greeting){const name=greeting.textContent.split(',').at(-1).trim();const hour24=period.toLowerCase()==='pm'&&hour!==12?hour+12:period.toLowerCase()==='am'&&hour===12?0:hour;const salutation=hour24<12?'Good morning':hour24<17?'Good afternoon':hour24<22?'Good evening':'Good night';greeting.textContent=`${salutation}, ${name}`}};tick();setInterval(tick,1000)}
function chart(id, type, color){const el=document.getElementById(id);if(!el)return;new Chart(el,{type,data:{labels:JSON.parse(el.dataset.labels||'["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]'),datasets:[{data:JSON.parse(el.dataset.values),borderColor:color,backgroundColor:color+'33',fill:true,tension:.4,borderWidth:2}]},options:{plugins:{legend:{display:false}},scales:{x:{grid:{display:false},ticks:{color:'#99a5a2'}},y:{beginAtZero:true,grid:{color:'#273230'},ticks:{color:'#99a5a2'}}}}})}
const weekly=document.getElementById('weeklyChart');if(weekly){weekly.dataset.values=weekly.dataset.values;chart('weeklyChart','line','#c9f364')}chart('completionChart','line','#c9f364');chart('studyChart','bar','#f5a85b');chart('weightChart','line','#c9f364');
