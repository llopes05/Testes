package features;

import com.intuit.karate.junit5.Karate;

class TestRunner {
    
    @Karate.Test
    Karate testAll() {
        return Karate.run().relativeTo(getClass());
    }
    
    @Karate.Test
    Karate testTodos() {
        return Karate.run("todos").relativeTo(getClass());
    }
    
    @Karate.Test
    Karate testPosts() {
        return Karate.run("posts").relativeTo(getClass());
    }
    
    @Karate.Test
    Karate testUsers() {
        return Karate.run("users").relativeTo(getClass());
    }
    
    @Karate.Test
    Karate testComments() {
        return Karate.run("comments").relativeTo(getClass());
    }
}
