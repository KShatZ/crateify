import { Navigate, useLoaderData} from "react-router-dom";

import Header from "../components/authentication/Header";
import Form from "../components/authentication/Form";


export default function Login() {

    const isAuthenticated = useLoaderData();

    return (isAuthenticated ?
        
        <Navigate to="/" />
        :
        <>
            <Header />
            <Form isLogin={true} />
        </>
    )
}
