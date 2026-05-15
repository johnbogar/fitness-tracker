import { NavLink } from "react-router-dom";

export default function navItems({name, path}) {
    // function for creating our nav links
    //params 
    //name = string name of the nav item
    //path = the file path
    // outputs a react nav link
    
    return ( 
        <NavLink
            to={path}
            end={path === "/"}
            className={({ isActive }) => 
                isActive ? "link active" : "link"
            }
        >
            {name}
        </NavLink>
    );
}