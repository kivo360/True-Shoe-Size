/**
 * Get the address of the microservice.
 * @param isSSL - Determine if the address is going to include TLS (HTTPS) or not.
 */
export function getAddress(remotehost: string, remoteport: number, isSSL: boolean): string {
    let host = null
    let address = null
    
    if (remoteport === 80) {
        // Kill the port if it's not something interesting
        address = `${remotehost}`
    } else {
        address = `${remotehost}:${remoteport}`
    }


    if (isSSL === true) {
        host = `https://${address}`
    }else{
        host = `http://${address}`
    }
    
    return host
}