"use client";

import { useState, useEffect } from "react";
import PlotComponent from "../plot";
import { useDashboardContext } from "../context/DashboardContext";
import { loadModelImportances, loadModelStats } from "../load_data";
import { translations } from "../translations";

export default function ModelStatistics() {
  const { language, fetcher } = useDashboardContext();
  const [loading, setLoading] = useState(0);

  const [modelImportances, setModelImportances] = useState();
  const [modelStats, setModelStats] = useState();

  const t = translations[language];

  useEffect(() => {
    async function fetchData() {
      setLoading((prev) => prev + 1);
      try {
        await Promise.all([
          loadModelImportances(fetcher, setModelImportances),
          loadModelStats(fetcher, setModelStats),
        ]);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      }
      setLoading((prev) => prev - 1);
    }

    fetchData();
  }, [fetcher]);

  return (
    <>
      <h2>{t["modelStatistics"]}</h2>

      <div className="modelPlots">
        <div className="modelImportances">
          <PlotComponent
            t={t}
            isLoading={loading}
            type="model importances"
            data={modelImportances}
          />
        </div>
        <div className="modelStats">
          <PlotComponent
            t={t}
            isLoading={loading}
            type="model stats"
            data={modelStats}
          />
        </div>
      </div>
    </>
  );
}
