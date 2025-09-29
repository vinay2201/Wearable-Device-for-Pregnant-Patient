#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>

// ---- Replace with your LoRa driver ----
int lora_send(const uint8_t* buf, size_t len) {
    // stub: send buffer over LoRa
    // return 0 on success
    return 0;
}
// ---------------------------------------

// Mock sensors (replace with real drivers)
float read_heart_rate()   { return 85.0f + (rand() % 600 - 300) / 100.0f; }   // ~85 +/- 3
float read_spo2()         { return 98.0f + (rand() % 100 - 50) / 100.0f; }    // ~98 +/- 0.5
float read_temp()         { return 36.8f + (rand() % 30 - 15) / 100.0f; }     // ~36.8 +/- 0.15
float read_env_temp()     { return 22.0f + (rand() % 200 - 100) / 100.0f; }   // ~22 +/- 1.0
float read_motion()       { return fabsf((rand() % 200 - 100) / 1000.0f); }   // 0..0.2

static void pack_float_le(uint8_t* dst, float v) {
    union { float f; uint8_t b[4]; } u;
    u.f = v;
    dst[0]=u.b[0]; dst[1]=u.b[1]; dst[2]=u.b[2]; dst[3]=u.b[3];
}

int main(void) {
    const char* device_id = "device-001"; //  up to you; could be in EEPROM
    srand((unsigned)time(NULL));

    while (1) {
        float hr = read_heart_rate();
        float spo2 = read_spo2();
        float temp = read_temp();
        float envt = read_env_temp();
        float motion = read_motion();

        // Binary payload: [hr][spo2][temp][env_temp][motion] (5 x float32 LE)
        uint8_t buf[20];
        pack_float_le(buf+0, hr);
        pack_float_le(buf+4, spo2);
        pack_float_le(buf+8, temp);
        pack_float_le(buf+12, envt);
        pack_float_le(buf+16, motion);

        // Send via LoRa
        (void)lora_send(buf, sizeof(buf));

        // Also print JSON over UART for edge bridge debugging
        printf("{\"deviceId\":\"%s\",\"hr\":%.2f,\"spo2\":%.2f,\"temp\":%.2f,\"env_temp\":%.2f,\"motion\":%.3f}\n",
               device_id, hr, spo2, temp, envt, motion);

        // crude delay
        for (volatile long i=0;i<5000000;i++);
    }
    return 0;
}
