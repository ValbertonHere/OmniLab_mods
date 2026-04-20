/// <reference types="wot-gameface-types" />
/// <reference types="wot-gameface-types/types/gameface-libs.d.ts" />
// @ts-nocheck

import cls from "classnames";
import React from "react";
import { createRoot } from "react-dom/client";
import { animated, useSpring } from "@react-spring/web";

import { MediaProvider } from "./MediaContext";

import { ModelObserver } from "gameface:model";
import { playSound } from "gameface:sound";

type Model = {
    standID: string;
    onFooterItemClick: (params: { standID: string }) => void;
    onCloseClick: () => void;
}

const enterAnim = {
    from: { x: 0, opacity: 0 },
    to:   { x: 0, opacity: 1 },
    config: { duration: 800, easing: t => (t < .5 ? 4*t*t*t : (t-1)*(2*t-2)*(2*t-2)+1) },
};

const AVAILABLE_STANDS_DESCRIPTIONS = {
    'graphics': 3,
    'ui_hngr': 2,
    'sounds': 1
}

const model = ModelObserver<Model>('LuganskHangarTravelGuideView');
const POITabMenuMode = Object.freeze({ Showed: "showed", Hidden: "hidden" });
const POITabSize = Object.freeze({ Small: "small", Big: "big" });

function CloseBtn() {
    return (
        <div className="closeBtn" onClick={() => {model.model?.onCloseClick()}}></div>
    );
}

function ViewHeader() {
    return (
        <div className="header">
            <div className="title">ЛУГАНСКИЙ АНГАР</div>
            <div id="subtitle">Место, где родилась легенда классики.</div>
        </div>
    );
}

function POIs({size = POITabSize.Small}) {
    const [mode, setMode] = React.useState(POITabMenuMode.Hidden)
    const [availableDescrs, setAvailableDescrs] = React.useState(1)
    const [activeTab, setActiveTab] = React.useState('main')
    const [activeDescr, setActiveDescr] = React.useState(1)

    const menu_classes = cls("POIs_tabmenu", `POIs_tabmenu_${mode}`);
    const arrow_classes = cls("POIs_arrow", `POIs_arrow_${mode}`)
    const tab_classes = cls("POIs_tab", `POIs_tab_${size}`);
    const main_text_classes = cls("POI_text", `POI_text_${size}`, `POI_text_${mode}`)
    const description_text_classes = cls("POI_description", `POI_description_${size}`, `POI_description_${mode}`)
    const next_button_classes = cls('POI_text', 'descr_button', `${activeDescr < availableDescrs ? 'descr_button_show' : 'descr_button_hide'}`, `descr_button_${mode}`)
    const back_button_classes = cls('POI_text', 'descr_button', `${activeDescr > 1 ? 'descr_button_show' : 'descr_button_hide'}`, `descr_button_${mode}`)

    function onArrowMouseEnter() {
        playSound('gui_hangar_hover')
        setMode(POITabMenuMode.Showed);
    }

    function onMenuMouseLeave() {
        playSound('gui_hangar_hover')
        setMode(POITabMenuMode.Hidden);
    }

    function onTabMouseEnter() {
        playSound('personal_reserves_hover');
    }

    function onTabClick(event) {
        const standID = event.target.id

        playSound('tank_selection');
        setMode(POITabMenuMode.Hidden);
        model.model?.onFooterItemClick({standID});
        setTimeout(() => {setActiveTab(standID); setActiveDescr(1); setAvailableDescrs(AVAILABLE_STANDS_DESCRIPTIONS[standID])}, 550) // Чтоб не сразу скрывал вкладку, а после скрытия её с экрана.
    }

    function onNextDescrClick() {
        setActiveDescr(activeDescr + 1)
    }

    function onBackDescrClick() {
        setActiveDescr(activeDescr - 1)
    }

    return (
        <div className="POIs">
            <div className={main_text_classes}>{R.strings.mto_lugansk_travel_guide[activeTab].shortDescription[`c_${activeDescr}`]()}</div>
            <div className={main_text_classes + description_text_classes} dangerouslySetInnerHTML={{ __html: R.strings.mto_lugansk_travel_guide[activeTab].description[`c_${activeDescr}`]() }}></div>
            <div className="buttons">
                <div className={back_button_classes} onClick={onBackDescrClick}>« Назад</div>
                <div className={next_button_classes} onClick={onNextDescrClick}>Далее »</div>
            </div>
            <div className={arrow_classes} onMouseEnter={onArrowMouseEnter} ></div>
            <div className={menu_classes} onMouseLeave={onMenuMouseLeave}>
                <div id="graphics" className={tab_classes + `${activeTab === 'graphics' ? ' POIs_tab_active' : ''}`} onClick={(event) => onTabClick(event)} onMouseEnter={onTabMouseEnter}>
                    <div className="tabTitle">ГРАФИКА</div>
                </div>
                <div id="ui_hngr" className={tab_classes + `${activeTab === 'ui_hngr' ? ' POIs_tab_active' : ''}`} onClick={(event) => onTabClick(event)} onMouseEnter={onTabMouseEnter}>
                    <div className="tabTitle">ИНТЕРФЕЙС И АНГАРЫ</div>
                </div>
                <div id="sounds" className={tab_classes + `${activeTab === 'sounds' ? ' POIs_tab_active' : ''}`} onClick={(event) => onTabClick(event)} onMouseEnter={onTabMouseEnter}>
                    <div className="tabTitle">ЗВУКИ</div>
                </div>
            </div>
        </div>
    )
}

function ViewFooter() {
    return (
        <footer>
            <div>Выберите точку, с которой хотите ознакомиться.</div>
        </footer>
    )
}

function onModelUpdated() {
    const header = document.querySelector('.header')
    const title = document.querySelector('.title')
    const subtitle = document.getElementById('subtitle')

    if (!title && !subtitle && !model.model) return;
    
    header.className = 'header header_description';
    title.textContent = R.strings.mto_lugansk_travel_guide[model.model?.standID].title();
    title.className = 'title title_description';
    subtitle.textContent = '';
}

function App() {

    // Pull dynamic data from the host’s model; here we just read from globals (original used observers)
    const [viewSize, setViewSize] = React.useState(viewEnv.getViewSizeRem());
    const ref = React.useRef(null);

    React.useEffect(() => {
        const handler = size => setViewSize(size);
        engine.on("screenResized", handler);
        return () => engine.off("screenResized", handler);
    }, []);

    // Inform host of input area (original did a double rAF)
    React.useEffect(() => {
        let raf = requestAnimationFrame(() => {
        raf = requestAnimationFrame(() => {
            const el = ref.current;
            if (!el) return;
            const rect = el.getBoundingClientRect();
            viewEnv.setInputArea(
            viewEnv.pxToRem(rect.left),
            viewEnv.pxToRem(rect.top),
            viewEnv.pxToRem(rect.width),
            viewEnv.pxToRem(rect.height),
            );
        });
        });
        return () => cancelAnimationFrame(raf);
    }, [viewSize]);

    const style = useSpring(enterAnim);
    const size = viewSize.width >= 1280 ? POITabSize.Big : POITabSize.Small;

    return (
        <animated.div className="App" style={style}>
            <CloseBtn />
            <ViewHeader />
            <POIs size={size}/>
            <ViewFooter />
        </animated.div>
    );
}

engine.whenReady.then(() => {
    const root = createRoot(document.getElementById('root'));

    root.render(
        <MediaProvider>
            <App />
        </MediaProvider>
    );

    model.onUpdate(() => {
        onModelUpdated();
    });
    model.subscribe();
})