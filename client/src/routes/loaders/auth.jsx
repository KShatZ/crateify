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
  const response = await fetch("/api/auth/user", {
      method: "GET",
      credentials: "include"
  });
  
  const status = response.status;

  // Request was not authenticated
  if (status != HTTP.OK && status != HTTP.SEE_OTHER) {
    return null;
  } 
  // Request is authenticated
  else {
    const body = await response.json();
    // User does not have Spotify authorized, redirect to Spotify oAuth page
    if (status == HTTP.SEE_OTHER) {
      return redirect(body.data.redirect_uri);
    } 
    return body.data;
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