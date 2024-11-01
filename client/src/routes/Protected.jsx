import { Outlet, Navigate, useLoaderData, ScrollRestoration } from "react-router-dom";

import { CurrentUser } from "../field_names";


export default function Protected() {
    
    const currentUser = useLoaderData();
    
    if (!currentUser) {
        return <Navigate to="/login/auth/false" />
    }

    return (
        <CurrentUser.Provider value={currentUser}>
            <ScrollRestoration />
            <Outlet />
        </CurrentUser.Provider>
    );
}