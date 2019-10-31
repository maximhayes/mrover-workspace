<template>
    <h1>If you see this, LCMEcho has been imported!</h1>
</template>

<script>
    /*to make your life easy debugging this, install https://github.com/vuejs/vue-devtools in ya browser
    this section establishes all variables linked to some inputs/outputs on screen
    all variables used to update DOM !!MUST!! be registered in this data: object before use*/
    import LCMBridge from 'lcm_bridge_client/dist/bridge.js'
    
    export default {
    name: 'LCMEcho',
    data () {
        return {
        lcm_: null,
        connections: {
            lcm: false
        },

        messages:[],
        viewing:{
          '/arm_control': false,
          '/arm_motors': false,
          '/arm_toggles_button_data': false,
          '/arm_toggles_toggle_data': false,
          '/auton': false,
          '/autonomous': false,
          '/camera_servos': false,
          '/config_pid': false,
          // '/course': false,
          '/debugMessage': false,
          '/drive_control': false,
          '/encoder': false,
          '/gps': false,
          '/ik_arm_control': false,
          '/ik_ra_control': false,
          '/imu': false,
          '/kill_switch': false,
          '/microscope': false,
          '/motor': false,
          '/nav_status': false,
          '/obstacle': false,
          '/odometry': false,
          '/pi_camera': false,
          '/pi_settings': false,
          '/sa_controls': false,
          '/sa_motors': false,
          '/sensor_switch': false,
          '/sensors': false,
          '/set_demand': false,
          '/temperature': false,
          '/tennis_ball': false
        },
        odom: {
            latitude_deg: 38,
            latitude_min: 24.38226,
            longitude_deg: -110,
            longitude_min: -47.51724,
            bearing_deg: 0,
            speed: 0
        },

        connections: {
            websocket: false,
            lcm: false,
            motors: false,
            cameras: [false, false, false, false, false, false]
        },

        nav_status: {
            completed_wps: 0,
            missed_wps: 0,
            total_wps: 0
        }
        }
    },

    methods: {
        publish: function (channel, payload) {
        this.lcm_.publish(channel, payload)
        },

        subscribe: function (channel, callbackFn) {
        if( (typeof callbackFn !== "function") || (callbackFn.length !== 1)) {
            console.error("Callback Function is invalid (should take 1 parameter)")
        }
        this.lcm_.subscribe(channel, callbackFn)
        }
    },

    created: function () {
        this.lcm_ = new LCMBridge(
        'ws://localhost:8020',
        // Update WebSocket connection state
        (online) => {
            this.lcm_.setHomePage()
            this.connections.websocket = online
        },
        // Update connection states
        (online) => {
            this.connections.lcm = online[0],
        },
        // Subscribed LCM message received
        (msg) => {
            if (msg.topic === '/odometry') {
            this.odom = msg.message
            } else if (msg.topic === '/kill_switch') {
            this.connections.motors = !msg.message.killed
            } else if (msg.topic === '/debugMessage') {
            if (msg['message']['isError']) {
                console.error(msg['message']['message'])
            } else {
                console.log(msg['message']['message'])
            }
            }
        },
        // Subscriptions
        [
            {'topic': '/odometry', 'type': 'Odometry'},
            {'topic': '/nav_status', 'type': 'NavStatus'},
            {'topic': '/gps', 'type': 'GPS'},
            {'topic': '/tennis_ball', 'type': 'TennisBall'},
            {'topic': '/obstacle', 'type': 'Obstacle'},
            {'topic': '/course', 'type': 'Course'}
        ]
        )
</script>
