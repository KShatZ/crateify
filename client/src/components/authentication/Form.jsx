import { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";

import "./styles.css";

export default function Form({ isLogin }) {

    const [ username, setUsername ] = useState("");
    const [ password, setPassword ] = useState("");
    const [ formMessage, setFormMessage ] = useState(null);

    const navigate = useNavigate();
    let location = useLocation();

    const classes = {
        default: "grey-border-2",
        message: "form-message grey-border-2"
    }

    useEffect(() => {
        if (isLogin && location.state) {
            if (location.state.userCreated) {
                /** After succesful account creation user is redirected to login
                 * page with success message. userCreated is added to the state object
                 * in order to determine whether or not to display a success message on
                 * login render. 
                 */
                if (!formMessage) {
                    setFormMessage({
                        error: false,
                        msg: "Account succesfully created, you may now login!"
                    });
                } else {
                    // Clear userCreated state after message shown
                    delete location.state.userCreated;
                }
            }
        }
    }, [isLogin, location, formMessage])
    
    function handleInput(event) {
        const inputName = event.target.name;
        let inputValue = event.target.value;
   
        switch (inputName) {
            case "username":
                setUsername(inputValue);
                break;
            case "password":
                setPassword(inputValue)
                break; 
            default:
                break;
        }
    }

    async function handleSubmit(event) {
        event.preventDefault();

        // Todo: Better input validation
        if (username.length == 0 || password.length == 0) {
            console.log("The username and password fields cannot be empty");
            return;
        }

        const userCredentials = {
            username: username,
            password: password
        }

        const endpoint = isLogin ? "login" : "register"; 

        // Todo: Create own request interface
        try {
            const response = await fetch(`/api/${endpoint}`, {
                method: "POST",
                body: JSON.stringify(userCredentials),
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include",
            });

            const body = await response.json();

            if (endpoint == "login") { 
                // TODO
                switch(response.status) {

                    case 200:
                        // Redirect to dashboard
                        navigate("/")
                        break;

                    
                    // User provided invalid credentials
                    case 400:
                        setFormMessage({
                            error: true,
                            msg: body.error.msg
                        });
                        break;

                    // Some server error
                    case 500:
                        setFormMessage({
                            error: true,
                            msg: body.error.msg
                        });  
                        break;
                    default:
                        break;
                }
            } else {
                switch(response.status) {

                    // User created succesfully
                    case 201:      
                        navigate("/login", {
                            state: {
                                userCreated: true
                            }
                        });
                        break; 
                    
                    // User provided invalid input
                    case 400:
                        setFormMessage({
                            error: true,
                            msg: body.error.msg
                        });
                        break;

                    // User already exists - eventually remove
                    case 409: 
                        setFormMessage({
                            error: true,
                            msg: body.error.msg
                        });
                        break;

                    // Some server error
                    case 500:
                        setFormMessage({
                            error: true,
                            msg: body.error.msg
                        });  
                        break;
                    default:
                        break;
                }
            }
        } catch(e) {

            let message;
            if (endpoint == "login") {
                message = "There was an issue logging you in on our end, please try again later.";
            } else {
                message = "There was an issue creating your account on our end, please try again later.";
            }

            setFormMessage({
                error: true,
                msg: message
            });
        }
    }

    // Register request:
    //  - 201: User created
    //  - 400: Invalid Input
    //  - 409: User already exists
    //  - 500: Some server error

    // Login request:
    //  - 200: User logged in
    //  - 400: Bad username and/or password
    //  - 401: Need to setup Spotify oAuth
    //  - 500: Some issue logging in


    return (
        <div id="auth-form-container" className="container">
            <form 
                id="auth-form" 
                className={ formMessage ? classes.message : classes.default }
                onSubmit={ handleSubmit }
            >

                <h1>{ isLogin ? "Login:":"Register:" }</h1>

                <div id="auth-form-inputs">
                    <div id="auth-input-group">
                        <label htmlFor="username">Username:</label>
                        <input className="bg-color txt-color grey-border-2"
                            id="username"
                            name="username"
                            value={ username }
                            type="text"
                            onChange={ handleInput }
                        />
                    </div>

                    <div id="auth-input-group">
                        <label htmlFor="password">Password:</label>
                        <input className="bg-color txt-color grey-border-2"
                            id="password"
                            name="password"
                            value={ password }
                            type="password"
                            onChange={ handleInput }
                        />
                    </div>
                </div>

                { formMessage && 
                    <p id="auth-form-msg" className={ formMessage.error ? "error-msg" : "success-msg" }>
                        { formMessage.msg }
                    </p> 
                }

                <button type="submit" style={ isLogin ? {}:{width:"65%"} }>{ isLogin ? "Login":"Create Account" }</button>

                { isLogin ? 
                    <div id="auth-redirect">
                        <p>Dont have an account?</p>
                        <Link to="/register">Create Account</Link>
                    </div>
                    :
                    <div id="auth-redirect">
                        <p>Already have an account?</p>
                        <Link to="/login">Login</Link>
                    </div>
                }
            </form>
        </div>
       
    )
}
