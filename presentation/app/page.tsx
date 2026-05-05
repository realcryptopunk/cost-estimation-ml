"use client";

import { SlideProvider } from "../components/SlideProvider";
import { SlideProgress } from "../components/SlideProgress";
import { TitleSlide } from "../components/slides/TitleSlide";
import { ProblemSlide } from "../components/slides/ProblemSlide";
import { DataSlide } from "../components/slides/DataSlide";
import { FeaturesSlide } from "../components/slides/FeaturesSlide";
import { ModelsSlide } from "../components/slides/ModelsSlide";
import { KeyFindingSlide } from "../components/slides/KeyFindingSlide";
import { AblationSlide } from "../components/slides/AblationSlide";
import { RegionalSlide } from "../components/slides/RegionalSlide";
import { ShapSlide } from "../components/slides/ShapSlide";
import { ShapRegionalSlide } from "../components/slides/ShapRegionalSlide";
import { SignificanceSlide } from "../components/slides/SignificanceSlide";
import { LimitationsSlide } from "../components/slides/LimitationsSlide";
import { FutureSlide } from "../components/slides/FutureSlide";
import { AppScanSlide } from "../components/slides/AppScanSlide";
import { AppEstimateSlide } from "../components/slides/AppEstimateSlide";
import { AppReportSlide } from "../components/slides/AppReportSlide";
import { ThankYouSlide } from "../components/slides/ThankYouSlide";

const TOTAL_SLIDES = 17;

export default function Home() {
  return (
    <SlideProvider total={TOTAL_SLIDES}>
      <div className="relative h-screen w-screen overflow-hidden bg-eggshell">
        <TitleSlide />
        <ProblemSlide />
        <DataSlide />
        <FeaturesSlide />
        <ModelsSlide />
        <KeyFindingSlide />
        <AblationSlide />
        <RegionalSlide />
        <ShapSlide />
        <ShapRegionalSlide />
        <SignificanceSlide />
        <LimitationsSlide />
        <FutureSlide />
        <AppScanSlide />
        <AppEstimateSlide />
        <AppReportSlide />
        <ThankYouSlide />
        <SlideProgress />
      </div>
    </SlideProvider>
  );
}
