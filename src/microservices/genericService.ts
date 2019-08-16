/**
 * Get the address of the microservice.
 * @param isSSL - Determine if the address is going to include TLS (HTTPS) or not.
 */
export function getAddress(remotehost: string, remoteport: number, isSSL: boolean): string {
    let host = ""

    if (remotehost === "localhost") {
        if (remoteport === 80) {
            // Kill the port if it's not something interesting
            return `${remotehost}`
        }
        // Otherwise return the localhost and regression port 
        return `${remotehost}:${remoteport}`
    }


    if (isSSL === true) {
        host = "https"
        if (remoteport === 80) {
            // Kill the port if it's not something interesting
            return `${host}://${remotehost}`
        }
        return `${host}://${remotehost}:${remoteport}`
    }
    host = "http"
    if (remoteport === 80) {
        // Kill the port if it's not something interesting
        return `${host}://${remotehost}`
    }
    return `${host}://${remotehost}:${remoteport}`
}