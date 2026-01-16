export interface Translation {
  title: string;
  subtitle: string;
  charts: {
    weeklyTraffic: string;
    monthlyTraffic: string;
    eventImpact: string;
  };
  dotw: string[];
  months: string[];
  det_anal: string;
}

export const translations: Record<string, Translation> = {
  en: {
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
    det_anal: "DETAILED ANALYSIS",
  },
};
