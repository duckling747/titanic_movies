
const defaultPassword = "salainen";
const makeRandomUname = () => {
    const characterset =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖabcdefghijklmnopqrstuvwxyzåäö123456789";
    let result = "";
    for (let i = 0; i < 8; ++i) {
        result += characterset
            .charAt(Math.floor(Math.random() * characterset.length));
    }
    return result;
};

const adminuname = "testadmin";

let existingUsernames = [];

before(() => {
    // create testing admin account if not exists
    cy.visit("/testing");
});

const login = (uname) => {
    cy.contains("Login").click();
    cy.get("input#username")
        .type(uname);
    cy.get("input#password").type(defaultPassword);
    cy.contains("input", "Sign In").click();
};

describe("Basic functionality", () => {
    beforeEach(() => {
        cy.visit("/");
    });
    it("welcomes you", () => {
        cy.contains("Welcome");
    });
    it("allows registering with reasonable credentials", () => {
        cy.contains("Register").click();
        existingUsernames.push(makeRandomUname());
        cy.get("input#username")
            .type(existingUsernames[existingUsernames.length-1]);
        cy.get("input#password").type(defaultPassword);
        cy.get("input#password2").type(defaultPassword);
        cy.contains("input", "Register").click();
        cy.contains("succes");
    });
    it("allows logging in with an existing username", () => {
        login(existingUsernames[existingUsernames.length-1]);
        cy.contains(
            `Logged in as ${existingUsernames[existingUsernames.length-1]}`);
    });
    it("allows logging out", () => {
        login(existingUsernames[existingUsernames.length-1]);
        cy.contains("Logout").click();
        cy.contains(
            `Logged in as ${existingUsernames[existingUsernames.length-1]}`
        ).should("not.exist");
    });
});

const movieName = "Pocahontas";
const movieYear = "1995";
const movieSynopsis = "It\'s the one where the blonde guy comes to America and stuff happends with the indians there.";

describe("Basic admin functionality", () => {
    beforeEach(() => {
        cy.visit("/");
        login(adminuname);
    });
    it("allows logging with testing admin account", () => {
        cy.contains(
            `Logged in as ${adminuname}`);
    });
    it("allows admins to add movies", () => {
        cy.visit("/admin");
        cy.contains("a", "Movies").click();
        cy.get("input#title").type(movieName);
        cy.get("input#year").type(movieYear);
        cy.get("input#synopsis")
            .type(movieSynopsis);
        cy.contains("input", "Add Movie").click();
        cy.contains(movieName);
        cy.contains(movieYear);
        cy.contains(movieSynopsis.substring(0, 10));
    });
    it("shows added movies in Browse movies view", () => {
        cy.contains("Browse movies").click();
        cy.contains(movieName);
        cy.contains(movieYear);
    });
});

describe("Review functionality", () => {
    const reviewGrade = "3";
    const reviewThoughts = "My thoughts are exactly such as these.";
    const reviewFeels = "My feelings abound, like the night sky grazing upon the featherless moon.";

    beforeEach(() => {
        cy.visit("/");
        login(existingUsernames[existingUsernames.length-1]);
    });
    it("allows to review existing movies and find the added review", () => {
        cy.contains("Browse movies").click();
        cy.contains(movieName).click();
        cy.get("input#grade").type(reviewGrade);
        cy.get("textarea#thoughts").type(reviewThoughts);
        cy.get("textarea#feelings").type(reviewFeels);
        cy.contains("input", "Send").click();
        cy.contains("Review sent succesfully");
        cy.contains("a", "Read all reviews").click();
        cy.get("input#textcontains").type(reviewThoughts);
        cy.contains("input", "Apply").click();
        cy.contains(`${reviewGrade}/5`);
        cy.contains(reviewThoughts);
        cy.contains(reviewFeels);
    });
});

describe("Basic access control", () => {
    beforeEach(() => {
        cy.visit("/");
    });
    it("doesn't allow viewing movies w/out logging in", () => {
        cy.contains("Browse movies").click();
        cy.contains(movieName).click();
        cy.contains("Please log in to access this page.");
        cy.contains("Login");
    });
    it("doesn't allow to just brazenly waltz into admin view", () => {
        cy.visit("/admin", { failOnStatusCode: false });
        cy.contains("Access denied.");
    });
    it("...not even when logged in", () => {
        login(existingUsernames[existingUsernames.length-1]);
        cy.visit("/admin", { failOnStatusCode: false });
        cy.contains("Access denied.");
    });
    it("...not on any admin site", () => {
        login(existingUsernames[existingUsernames.length-1]);
        const adminSites = ["/admin/movies", "/admin/users", "/admin/actors",
            "/admin/genres", "/admin/languages", "/admin/movie_requests"];
        for (const each of adminSites) {
            cy.visit(each, { failOnStatusCode: false });
            cy.contains("Access denied.");
        }
    });
});
