import React from "react";
import cls from "classnames";
import { createRoot } from "react-dom/client";
import { animated, useSpring } from "@react-spring/web";

const enterAnim = {
    from: { x: 535 },
    to:   { x: 0 },
    config: { duration: 800, easing: t => (t < .5 ? 4*t*t*t : (t-1)*(2*t-2)*(2*t-2)+1) },
};

function UserCustomizationStylesCarouselItem({styleName=''}) {
    return (<div className="stylesCarouselItem">{styleName}</div>)
}

function UserCustomizationView() {
    const style = useSpring(enterAnim);

    return (<animated.div className="placeholder" style={style}>
        <div className="viewLabel">АГРЕГАТОР СТИЛЕЙ ДЛЯ</div>
        <div className="viewLabel">ИС-7</div>
        <div className="carousel">
            <UserCustomizationStylesCarouselItem styleName="Стиль твоей мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль твоей мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль твоей мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
            <UserCustomizationStylesCarouselItem styleName="Стиль мо мамки"/>
        </div>
    </animated.div>)
}

function App() {

    // Pull dynamic data from the host’s model; here we just read from globals (original used observers)
    // const [viewSize, setViewSize] = React.useState(viewEnv.getViewSizeRem());
    // const ref = React.useRef(null);

    // React.useEffect(() => {
    //     const handler = size => setViewSize(size);
    //     engine.on("screenResized", handler);
    //     return () => engine.off("screenResized", handler);
    // }, []);

    // // Inform host of input area (original did a double rAF)
    // React.useEffect(() => {
    //     let raf = requestAnimationFrame(() => {
    //     raf = requestAnimationFrame(() => {
    //         const el = ref.current;
    //         if (!el) return;
    //         const rect = el.getBoundingClientRect();
    //         viewEnv.setInputArea(
    //         viewEnv.pxToRem(rect.left),
    //         viewEnv.pxToRem(rect.top),
    //         viewEnv.pxToRem(rect.width),
    //         viewEnv.pxToRem(rect.height),
    //         );
    //     });
    //     });
    //     return () => cancelAnimationFrame(raf);
    // }, [viewSize]);

    // const size = viewSize.width >= 1280 ? POITabSize.Big : POITabSize.Small;

    return (
        <animated.div className="App">
            <UserCustomizationView />
        </animated.div>
    );
}

window.onload = (() => {
    const root = createRoot(document.getElementById('root'));

    root.render(
        <App />
    );
})