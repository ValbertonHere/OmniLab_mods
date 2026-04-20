import { playSound } from 'gameface:sound';
import { ModelObserver } from 'gameface:model';
import { createCButton } from '../../shared_sources/js/utils/elements';

// viewEnv.resizeViewPx(80, 80); <- Можно выставить вручную размер вьюшки.
// viewEnv.setHitAreaPaddingsRem(1e5, 1e5, 1e5, 1e5, 15); <- Определяет область взаимодействия с вьюшкой.

type Model = {
  name: string | null;
}

const model = ModelObserver<Model>('VAL_TEST');


function init() {
    playSound('debug_event');
}

function createButton() {
	const testButton = document.createElement("div");

	testButton.className = "testButton";
	testButton.addEventListener("click", () => {
		playSound("error_event");
	});

	const testButtonIcon = document.createElement("div");
	testButtonIcon.className = "testButtonIcon";

  const testButtonText = document.createElement("div");
  testButtonText.className = "testButtonText";
  testButtonText.textContent = "VAL_TEST512";

	testButton.appendChild(testButtonIcon);
	testButton.appendChild(testButtonText);

	return testButton;
}

engine.whenReady.then(() => {
    const observer = new MutationObserver(init);
    observer.observe(document.body, {childList: true, subtree: true});
    console.warn('test');
    const crew_list = document.getElementById("crew_widget_slots_list");
    const widget = crew_list?.parentNode;

    if (!widget) return;

    widget.insertBefore(createCButton("TEST", 200), crew_list)
    widget.insertBefore(createButton(), crew_list)
})