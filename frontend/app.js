// Demonstration values only. They are not generated from the selected photo.
const foods = [
  { name: 'Grilled chicken', kcal: 1.65, protein: .31, carbs: 0, fat: .036 },
  { name: 'White rice', kcal: 1.30, protein: .027, carbs: .282, fat: .003 },
  { name: 'Broccoli', kcal: .35, protein: .024, carbs: .072, fat: .004 },
  { name: 'Avocado', kcal: 1.60, protein: .02, carbs: .085, fat: .147 },
  { name: 'Egg', kcal: 1.55, protein: .13, carbs: .011, fat: .11 },
];
let items = [{ food: 0, grams: 120 }, { food: 1, grams: 160 }, { food: 2, grams: 80 }];
const $ = (id) => document.getElementById(id);
const format = (number) => `${number.toFixed(1)} g`;

function render() {
  $('items').replaceChildren();
  const totals = { kcal: 0, protein: 0, carbs: 0, fat: 0 };
  items.forEach((item, index) => {
    const food = foods[item.food];
    for (const key of Object.keys(totals)) totals[key] += food[key] * item.grams;
    const row = document.createElement('div'); row.className = 'item';
    const label = document.createElement('div'); label.className = 'item-name';
    label.textContent = food.name;
    const sub = document.createElement('small'); sub.className = 'item-sub'; sub.textContent = `${Math.round(food.kcal * item.grams)} kcal · sample estimate`;
    label.append(sub);
    const input = document.createElement('input'); input.type = 'number'; input.min = '0'; input.max = '5000'; input.step = '1'; input.value = item.grams; input.setAttribute('aria-label', `${food.name} grams`);
    input.addEventListener('input', () => { const grams = Number(input.value); if (Number.isFinite(grams) && grams >= 0 && grams <= 5000) { item.grams = grams; renderTotals(); } });
    const remove = document.createElement('button'); remove.type = 'button'; remove.textContent = '×'; remove.setAttribute('aria-label', `Remove ${food.name}`);
    remove.addEventListener('click', () => { items.splice(index, 1); render(); });
    row.append(label, input, remove); $('items').append(row);
  });
  renderTotals(totals);
}

function renderTotals(precomputed) {
  const totals = precomputed || items.reduce((sum, { food, grams }) => {
    for (const key of Object.keys(sum)) sum[key] += foods[food][key] * grams;
    return sum;
  }, { kcal: 0, protein: 0, carbs: 0, fat: 0 });
  $('total-calories').textContent = Math.round(totals.kcal);
  $('total-protein').textContent = format(totals.protein);
  $('total-carbs').textContent = format(totals.carbs);
  $('total-fat').textContent = format(totals.fat);
  document.querySelectorAll('.item').forEach((row, index) => {
    row.querySelector('.item-sub').textContent = `${Math.round(foods[items[index].food].kcal * items[index].grams)} kcal · sample estimate`;
  });
}

foods.forEach((food, index) => { const option = document.createElement('option'); option.value = index; option.textContent = food.name; $('food-select').append(option); });
$('add-form').addEventListener('submit', (event) => { event.preventDefault(); items.push({ food: Number($('food-select').value), grams: 100 }); render(); });
$('photo-input').addEventListener('change', (event) => {
  const file = event.target.files?.[0]; if (!file) return;
  if (!['image/png', 'image/jpeg'].includes(file.type)) { alert('Choose a PNG or JPEG image.'); event.target.value = ''; return; }
  const reader = new FileReader();
  reader.onload = () => { $('preview').src = reader.result; $('preview').hidden = false; $('upload-hint').hidden = true; };
  reader.readAsDataURL(file);
});
render();
