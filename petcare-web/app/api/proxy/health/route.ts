import { NextResponse } from "next/server";

const UPSTREAM = "https://api.myveticare.com/health";
const TIMEOUT_MS = 8000;

export async function GET() {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const upstream = await fetch(UPSTREAM, {
      signal: controller.signal,
      cache: "no-store",
      headers: { "User-Agent": "petcare-web-proxy/1.0" },
    });

    const body = await upstream.json();

    return NextResponse.json(body, { status: upstream.status });
  } catch (err) {
    const message = err instanceof Error ? err.message : "upstream_error";
    return NextResponse.json(
      { status: "error", error: message },
      { status: 502 }
    );
  } finally {
    clearTimeout(timer);
  }
}
