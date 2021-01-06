const https = require('https')

const hostname = 'mcss.utmrobotics.com'
const path = '/api/challenge'

const challengeRanks = [0, 1]

let i = -1

console.log('Running challenger. 400 BAD REQUEST is when there is nothing to challenge')

function challenge() {
    console.log('Challenging... ')
    i++
    if (i >= challengeRanks.length) i = 0
    const data = JSON.stringify({
        'target_rank': challengeRanks[i]
    })
    const req = https.request({
        hostname: hostname,
        path: path,
        port: 443,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': data.length,
            'Cookie': 'session=eyJsb2dnZWRfaW4iOnRydWUsInVzZXJuYW1lIjoibmljaG9sLndvbmdAbWFpbC51dG9yb250by5jYSJ9.X_T4iA.oM2AsBUBBQ8CaKUEdOY6kAELqKA'
        }
    }, res => {
        res.on('data', d => {
            console.log(`Req for: ${rank} code: ${res.statusCode} (${res.statusMessage})`)
        })
    })
    req.write(data)
    req.end()
}

setInterval(() => {
    challenge()
}, 1000 * 60 * 10)
challenge()