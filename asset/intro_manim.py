from manim import *


class IntroText(Scene):
    def construct(self):
        self.camera.background_color = "#0b1a2b"

        title = Text("test", font="Montserrat", color="#f2f2f2").scale(2.2)
        glow = Text("test", font="Montserrat", color="#4fd1ff").scale(2.35)
        glow.set_opacity(0.35)

        self.play(FadeIn(glow, shift=DOWN * 0.2, scale=1.05), run_time=0.8)
        self.play(Write(title), run_time=1.3)

        self.play(
            title.animate.shift(UP * 0.2).scale(1.02),
            glow.animate.shift(UP * 0.25).scale(1.02).set_opacity(0.5),
            run_time=1.0,
        )

        self.wait(0.6)
        self.play(FadeOut(title), FadeOut(glow), run_time=0.8)
