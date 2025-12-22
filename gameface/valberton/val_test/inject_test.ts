import { playSound } from 'gameface:sound';
import { ModelObserver } from 'gameface:model';

type Model = {
  request: string | null;
  sendCommand: (params: { command: string }) => void;
}


const model = ModelObserver<Model>('VAL_TEST');

function init() {
  const header = document.querySelector('[class*="Header_base"]');
  const footer = document.querySelector('[class*="App_footer"]');

  if (!header) return;
  if (!footer) return;
  
  header.textContent = R.strings.userCustomization.button.goToUserCustomization.label();
  footer.textContent = 'VAL_TEST32';
}

function test() {
  playSound('debug_event');
  const statistics = document.querySelector('[class*="Content_base"]');

  const test_title = document.createElement("div");
  test_title.textContent = "VAL_TEST128";

  statistics?.insertAdjacentElement('beforebegin', test_title);

}

engine.whenReady.then(() => {
    const observer = new MutationObserver(init);
    observer.observe(document.body, {childList: true, subtree: true});
    setTimeout(test, 0.5);
})