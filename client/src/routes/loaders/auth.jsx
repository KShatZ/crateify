import { redirect } from "react-router-dom";

import { HTTP } from "../../field_names";


/** 
 * Sends a request to the backends authentication check
 * endpoint /auth/user. Returns true if request is properly
 * authenticated, false otherwise. If user has not allowed 
 * access to Spotify data (oAuth) then redirect to auth page.
*/
export async function authLoader() {

  // TODO: Try/Catch
  const response = await fetch("/api/auth/validate", {
      method: "GET",
      credentials: "include"
  });
  
  const status = response.status;
  switch(status) {  

    case(HTTP.OK): {
      const responseBody = await response.json();
      return responseBody.data;
    }

    case (HTTP.UNAUTHORIZED): 
      return null

    case(HTTP.SEE_OTHER): {
      // Authorized but missing tokens
      const responseBody = await response.json();
      return redirect(responseBody.data.redirect_url);
    }

    case(HTTP.SERVER_ERROR): // TODO
      return null;

    default:
      return null;
  }
}


export async function logoutUser() {

  // TODO: Try/Catch
  const response = await fetch("/api/logout", {
    method: "POST",
    credentials: "include",
  });

  return redirect("/login")
}