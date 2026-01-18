const en = {
  title: "Mobility in Barcelona",
  subtitle: "Real-time analysis of city movement",
  charts: {
    weeklyTraffic: "Weekly Traffic Intensity",
    monthlyTraffic: "Monthly Traffic Trends",
    eventImpact: "Average Event Impact",
  },
  dotw: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  months: [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ],
  detAnal: "DETAILED ANALYSIS",
  workday: "workday",
  holiday: "holiday",
  modelStatistics: "MODEL STATISTICS",
};

export type Translation = typeof en;

export const translations: Record<string, Translation> = {
  en: en,
};
