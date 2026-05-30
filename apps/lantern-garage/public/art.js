const cards = Array.from(document.querySelectorAll(".art-card"));
const activeKicker = document.getElementById("activeKicker");
const activeTitle = document.getElementById("activeTitle");
const activeCopy = document.getElementById("activeCopy");
let activeIndex = 0;

function setActivePanel(index) {
  activeIndex = (index + cards.length) % cards.length;
  cards.forEach((card, cardIndex) => {
    const active = cardIndex === activeIndex;
    card.classList.toggle("active", active);
    card.setAttribute("aria-selected", active ? "true" : "false");
    card.tabIndex = active ? 0 : -1;
  });
  const card = cards[activeIndex];
  activeKicker.textContent = `Panel ${card.dataset.panel}`;
  activeTitle.textContent = card.dataset.title;
  activeCopy.textContent = card.dataset.copy;
  card.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
}

document.getElementById("prevPanel").addEventListener("click", () => setActivePanel(activeIndex - 1));
document.getElementById("nextPanel").addEventListener("click", () => setActivePanel(activeIndex + 1));

cards.forEach((card, index) => {
  card.addEventListener("click", () => setActivePanel(index));
});

document.addEventListener("keydown", (event) => {
  if (event.key === "ArrowLeft") setActivePanel(activeIndex - 1);
  if (event.key === "ArrowRight") setActivePanel(activeIndex + 1);
});

setActivePanel(0);
