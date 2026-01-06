package features;

import com.intuit.karate.junit5.Karate;

class TestRunner {
    
    @Karate.Test
    Karate testAll() {
        return Karate.run().relativeTo(getClass());
    }
    
    @Karate.Test
    Karate testUsuarios() {
        return Karate.run("usuarios").relativeTo(getClass());
    }
    
    @Karate.Test
    Karate testCentros() {
        return Karate.run("centros").relativeTo(getClass());
    }
    
    @Karate.Test
    Karate testEspacos() {
        return Karate.run("espacos").relativeTo(getClass());
    }
    
    @Karate.Test
    Karate testAgendas() {
        return Karate.run("agendas").relativeTo(getClass());
    }
    
    @Karate.Test
    Karate testReservas() {
        return Karate.run("reservas").relativeTo(getClass());
    }
}
