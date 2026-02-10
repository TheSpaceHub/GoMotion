"use server";
import pool from "./db";
import { QueryResult } from "pg";
import { RefObject } from "react";
import { Fetcher } from "./page";

export async function getMapData(day: any) {
  const result: QueryResult<any> = await pool.query(
    `
    with z as
    (select barri, stddev_samp(intensity) as std, avg(intensity) as mean
    from display_data
    group by barri)
    select d.barri, d.intensity, (d.intensity - z.mean) / z.std as zscore
    from display_data d, z
    where d.day = $1 and z.barri = d.barri
    `,
    [day],
  );
  return result.rows;
}

export async function getTableData(day: any) {
  const result: QueryResult<any> = await pool.query(
    `
    with z as
    (select barri, stddev_samp(intensity) as std, avg(intensity) as mean
    from display_data
    group by barri)
    select d.barri, d.intensity, z.mean, d.intensity / g.superficie as density, (d.intensity - z.mean) / z.std as zscore
    from display_data d, geospatial_data g, z
    where d.barri = z.barri and g.nom_barri = d.barri and d.day = $1
    `,
    [day],
  );
  return result.rows;
}

export async function getWeeklyTraffic(barri: string) {
  const result: QueryResult<any> = await pool.query(
    `
    SELECT AVG(intensity), EXTRACT(ISODOW FROM DATE(day)) AS dotw
    FROM display_data
    WHERE barri=$1
    GROUP BY dotw ORDER BY dotw
    `,
    [barri],
  );
  return result.rows;
}

export async function getMonthlyTraffic(barri: string) {
  const result: QueryResult<any> = await pool.query(
    `
    SELECT AVG(intensity), EXTRACT(MONTH FROM DATE(day)) AS month
    FROM display_data
    WHERE barri=$1
    GROUP BY month ORDER BY month
    `,
    [barri],
  );
  return result.rows;
}

export async function getAverageEventImpact(barri: string) {
  const result: QueryResult<any> = await pool.query(
    `
    SELECT e.category, AVG(d.intensity)
    FROM display_data d, events e
    WHERE d.barri=$1 and d.day = e.day
    GROUP BY e.category
    `,
    [barri],
  );
  return result.rows;
}

export async function getRainIntensityCorrelation(barri: string) {
  const result: QueryResult<any> = await pool.query(
    `
    SELECT d.precipitation_sum AS rain, d.intensity, d.day
    FROM display_data d
    WHERE d.barri=$1
    `,
    [barri],
  );
  return result.rows;
}

export async function getWorkdayVsHoliday(barri: string) {
  const result: QueryResult<any> = await pool.query(
    `
    SELECT intensity, is_holiday
    FROM display_data 
    WHERE barri=$1
    `,
    [barri],
  );
  return result.rows;
}

export async function getIntensityPerArea() {
  const result: QueryResult<any> = await pool.query(`
    SELECT g.nom_barri, g.superficie, AVG(d.intensity)
    FROM geospatial_data g, display_data d
    WHERE g.nom_barri = d.barri
    GROUP BY g.nom_barri, g.superficie
    `);
  return result.rows;
}

export async function getWeeklyIntensityDiff() {
  const result: QueryResult<any> = await pool.query(`
    with averages as ( 
    select d.barri, avg(d.intensity) as intensity
    from display_data d
    group by d.barri
    )
    select EXTRACT(ISODOW FROM DATE(day)) AS dotw, 100 * avg(d.intensity / a.intensity - 1) as avg
    from display_data d, averages a
    where d.barri = a.barri
    group by dotw order by dotw
    `);
  return result.rows;
}

export async function getMonthlyIntensityDiff() {
  const result: QueryResult<any> = await pool.query(`
    with averages as ( 
    select d.barri, avg(d.intensity) as intensity
    from display_data d
    group by d.barri
    )
    select EXTRACT(MONTH FROM DATE(day)) AS month, 100 * avg(d.intensity / a.intensity - 1) as avg
    from display_data d, averages a
    where d.barri = a.barri
    group by month order by month
    `);
  return result.rows;
}

export async function getModelImportances() {
  const result: QueryResult<any> = await pool.query(`
    select *
    from importances_and_features
    `);
  return result.rows;
}

export async function getModelStats() {
  const result: QueryResult<any> = await pool.query(`
    select * 
    from metadata 
    where key = 'model_accuracy' or key = 'model_error_over' or key = 'model_error_under';
    `);
  return result.rows;
}

export async function getDailyData(day: any) {
  const result: QueryResult<any> = await pool.query(
    `
    select d.precipitation_sum, d.is_holiday, d.temperature_2m_max, d.temperature_2m_min, SUM(d.intensity) as tt
    from display_data d
    where d.day = $1
    group by d.precipitation_sum, d.is_holiday, d.temperature_2m_max, d.temperature_2m_min
    `,
    [day],
  );
  return result.rows;
}

export async function getEventData(day: any) {
  const result: QueryResult<any> = await pool.query(
    `
    select *
    from events e
    where e.day = $1
    `,
    [day],
  );
  return result.rows;
}

export async function getFinalPredictedDate() {
  const result: QueryResult<any> = await pool.query(`
    select value
    from metadata
    where key = 'last_predicted_day'
    `);
  return result.rows;
}
