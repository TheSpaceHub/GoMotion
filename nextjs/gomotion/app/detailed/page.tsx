"use client";

import { useState, useEffect } from "react";
import PlotComponent from "../plot";
import { useDashboardContext } from "../context/DashboardContext";
import {
    loadWeeklyTraffic,
    loadMonthlyTraffic,
    loadAverageEventImpact,
    loadRainIntensityCorrelation,
    loadWorkdayVsHoliday,
    loadIntensityPerArea,
    loadWeeklyIntensityDiff,
    loadMonthlyIntensityDiff,
} from "../load_data";
import { translations } from "../translations";

export default function DetailedAnalytics() {
    const { barri, language, fetcher } = useDashboardContext();
    const [loading, setLoading] = useState(0);

    const [weeklyTraffic, setWeeklyTraffic] = useState();
    const [monthlyTraffic, setMonthlyTraffic] = useState();
    const [avgImpact, setAvgImpact] = useState();
    const [rainIntensityCorrelation, setRainIntensityCorrelation] = useState();
    const [workdayVsHoliday, setWorkdayVsHoliday] = useState();
    const [intensityPerArea, setIntensityPerArea] = useState();

    const [weeklyIntensityDiff, setWeeklyIntensityDiff] = useState();
    const [monthlyIntensityDiff, setMonthlyIntensityDiff] = useState();

    const t = translations[language];

    useEffect(() => {
        async function fetchData() {
            setLoading((prev) => prev + 1);
            try {
                await Promise.all([
                    loadWeeklyTraffic(fetcher, setWeeklyTraffic, barri),
                    loadMonthlyTraffic(fetcher, setMonthlyTraffic, barri),
                    loadAverageEventImpact(fetcher, setAvgImpact, barri),
                    loadRainIntensityCorrelation(fetcher, setRainIntensityCorrelation, barri),
                    loadWorkdayVsHoliday(fetcher, setWorkdayVsHoliday, barri),
                    loadIntensityPerArea(fetcher, setIntensityPerArea, barri),
                    loadWeeklyIntensityDiff(fetcher, setWeeklyIntensityDiff),
                    loadMonthlyIntensityDiff(fetcher, setMonthlyIntensityDiff),
                ]);
            } catch (error) {
                console.error("Failed to fetch data:", error);
            }
            setLoading((prev) => prev - 1);
        }

        fetchData();
    }, [barri]);

    return (
        <>
            <div className="title" style={{ marginTop: "-1rem" }}>
                <h2>
                    {barri ? `${t["detAnal"]}: ${barri.toUpperCase()}` : t["detAnal"]}
                </h2>
            </div>
            {barri ? (
                <div className="plots">
                    <div className="plot">
                        <PlotComponent t={t} isLoading={loading} type="weekly traffic" data={weeklyTraffic} />
                    </div>
                    <div className="plot">
                        <PlotComponent t={t} isLoading={loading} type="monthly traffic" data={monthlyTraffic} />
                    </div>
                    <div className="plot">
                        <PlotComponent t={t} isLoading={loading} type="average event impact" data={avgImpact} />
                    </div>
                    <div className="plot">
                        <PlotComponent t={t} isLoading={loading} type="rain/intensity correlation" data={rainIntensityCorrelation} />
                    </div>
                    <div className="plot">
                        <PlotComponent t={t} isLoading={loading} type="workday vs holiday" data={workdayVsHoliday} />
                    </div>
                    <div className="plot">
                        <PlotComponent t={t} isLoading={loading} type="intensity/area" data={intensityPerArea} />
                    </div>
                </div>
            ) : (
                <div style={{ padding: "2rem", textAlign: "center", color: "var(--foreground)", border: "1px solid var(--border)", borderRadius: "1rem", backgroundColor: "var(--background-sec)" }}>
                    <p>Please select a neighborhood from the Overview map to view detailed analytics.</p>
                </div>
            )}

            <div className="title" style={{ marginTop: "2rem" }}>
                <h2>{t["globalStats"]}</h2>
            </div>

            <div className="plots">
                <div className="plot">
                    <PlotComponent t={t} isLoading={loading} type="weekly intensity diff" data={weeklyIntensityDiff} />
                </div>
                <div className="plot">
                    <PlotComponent t={t} isLoading={loading} type="monthly intensity diff" data={monthlyIntensityDiff} />
                </div>
            </div>
        </>
    );
}
