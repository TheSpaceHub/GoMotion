"use server";
import pool from "./db";
import { QueryResult } from "pg";

export async function getData(day: any) {
  const result: QueryResult<any> = await pool.query(`
    SELECT * FROM importances_and_features
    `);
  return result.rows;
}

export async function getWeeklyTraffic(barri: string) {
  const result: QueryResult<any> = await pool.query(`
    SELECT AVG(intensity), EXTRACT(ISODOW FROM DATE(day)) AS dotw
    FROM display_data
    WHERE barri=$1
    GROUP BY dotw ORDER BY dotw
    `, [barri]);
  return result.rows;
}
