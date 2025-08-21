export function backoff(attempt: number) {
  const base = 500
  const max = 5000
  return Math.min(max, base * Math.pow(2, attempt))
}