import Header from "../components/authentication/Header";
import Form from "../components/authentication/Form";

export default function Register() {

    return (
    <>
        <Header />
        <Form isLogin={false}/>
    </>
    )
}