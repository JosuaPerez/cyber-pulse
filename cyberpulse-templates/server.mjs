import { createReadStream } from 'node:fs'
import { stat } from 'node:fs/promises'
import { createServer } from 'node:http'
import { dirname, extname, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), 'dist')
const port = Number.parseInt(process.env.PORT ?? '5173', 10)
const contentTypes = {
  '.css': 'text/css; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
}

function respond(response, status, body = '') {
  response.writeHead(status, {
    'Content-Type': 'text/plain; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'no-referrer',
  })
  response.end(body)
}

createServer(async (request, response) => {
  if (!['GET', 'HEAD'].includes(request.method ?? '')) {
    respond(response, 405, 'Method Not Allowed')
    return
  }

  let pathname
  try {
    pathname = decodeURIComponent(new URL(request.url ?? '/', 'http://localhost').pathname)
  } catch {
    respond(response, 400, 'Bad Request')
    return
  }

  const requested = resolve(root, `.${pathname === '/' ? '/index.html' : pathname}`)
  if (requested !== root && !requested.startsWith(`${root}${sep}`)) {
    respond(response, 404, 'Not Found')
    return
  }

  try {
    const metadata = await stat(requested)
    if (!metadata.isFile()) {
      respond(response, 404, 'Not Found')
      return
    }

    response.writeHead(200, {
      'Content-Type': contentTypes[extname(requested)] ?? 'application/octet-stream',
      'Content-Length': metadata.size,
      'Cache-Control': requested.endsWith('index.html')
        ? 'no-cache'
        : 'public, max-age=31536000, immutable',
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'Referrer-Policy': 'no-referrer',
    })
    if (request.method === 'HEAD') {
      response.end()
      return
    }
    createReadStream(requested).pipe(response)
  } catch {
    respond(response, 404, 'Not Found')
  }
}).listen(port, '0.0.0.0')
