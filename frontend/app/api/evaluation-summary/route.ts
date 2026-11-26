import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  try {
    // Check both potential locations (if running from frontend directory or project root)
    const candidatePaths = [
      path.resolve(process.cwd(), "..", "results", "evaluation_summary.json"),
      path.resolve(process.cwd(), "results", "evaluation_summary.json"),
    ];

    const summaryPath = candidatePaths.find((p) => fs.existsSync(p));

    if (!summaryPath) {
      return NextResponse.json(
        { error: "Stored evaluation summary file not found." },
        { status: 404 }
      );
    }

    const fileContent = fs.readFileSync(summaryPath, "utf-8");
    const data = JSON.parse(fileContent);
    return NextResponse.json(data);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json(
      { error: "Failed to read stored evaluation summary: " + message },
      { status: 500 }
    );
  }
}
