
import { LoggerService } from '@nestjs/common';



/**
 * We can add our own custom rules here. 
 * The custom rules can log into external services/servers so they can be viewed all in one place. 
 */
export class MyLogger implements LoggerService {
    log(message: string) { 
        console.log("Custom Log: ", message);
        console.log(message);        
    }
    error(message: string, trace: string) { 
        console.log("Custom Error: ", message);
        console.log(message);
        console.log(trace);
    }
    warn(message: string) { 
        console.log("Custom Warn: ", message);
        console.log(message);
    }
    debug(message: string) { 
        console.log("Custom Debug: ", message);
        console.log(message);
    }
    verbose(message: string) {
        console.log("Custom Verbose: ", message); 
        console.log(message);
    }
}