import { createContext } from "react";

// ------ React Contexts ------ //
export const CurrentUser = createContext();

// ----- Server Requests ----- //
export const HTTP = {
    OK: "200",
    CREATED: "201",

    SEE_OTHER: "303",

    BAD_REQUEST: "400",
    UNAUTHORIZED: "401",
    CONFLICT: "409",

    SERVER_ERROR: "500"
}
