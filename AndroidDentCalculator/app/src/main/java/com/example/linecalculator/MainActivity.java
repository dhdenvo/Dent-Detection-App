package com.example.linecalculator;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Environment;
import android.os.StrictMode;
import android.provider.MediaStore;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.location.Location;
import android.location.LocationManager;
import android.content.Context;
import android.widget.ImageView;


import com.android.volley.AuthFailureError;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

import pub.devrel.easypermissions.EasyPermissions;


public class MainActivity extends AppCompatActivity {

    private Button button;
    private TextView p, lastUpdate;
    private ImageView graph;
    private String encoded_string, image_name;
    private Bitmap bitmap;
    private File file;
    private Uri file_uri;
    private static String server = "http://drv-ctp6.canlab.ibm.com:5000/data";
    private String[] allPermissions = {android.Manifest.permission.READ_EXTERNAL_STORAGE, android.Manifest.permission.WRITE_EXTERNAL_STORAGE, android.Manifest.permission.ACCESS_FINE_LOCATION};


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        button = findViewById(R.id.camera);
        p = findViewById(R.id.people);
        lastUpdate = findViewById(R.id.wait);
        graph = findViewById(R.id.graph);

        StrictMode.VmPolicy.Builder builder = new StrictMode.VmPolicy.Builder();
        StrictMode.setVmPolicy(builder.build());

        if (EasyPermissions.hasPermissions(getApplicationContext(), allPermissions)) {
            Log.d("PERMISSIONS", "YAS QUEEN!");

        } else {
            EasyPermissions.requestPermissions(this, "Access for storage",
                    101, allPermissions);
        }

        new JSONTask().execute(server);
        new ImageTask().execute(server);

        Thread t = new Thread(){
            @Override
            public void run(){
                while (!isInterrupted()){
                    try {
                        Thread.sleep(5000);

                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                new JSONTask().execute(server);
                                new ImageTask().execute(server);
                            }
                        });

                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        };
        t.start();

        button.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                Intent i = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                getFileUri();
                i.putExtra(MediaStore.EXTRA_OUTPUT,file_uri);
                startActivityForResult(i,10);
            }
        });
    }

    private void getFileUri(){
        image_name = "testing123.jpg";
        file = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES)
                +File.separator+image_name);

        file_uri = Uri.fromFile(file);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {

        if(requestCode == 10 && resultCode == RESULT_OK){
            new Encode_image().execute();
        }
    }

    private class Encode_image extends AsyncTask<Void,Void,Void>{

        @Override
        protected Void doInBackground(Void... voids) {

            bitmap = BitmapFactory.decodeFile(file_uri.getPath());
            bitmap = BitmapFactory.decodeFile(file_uri.getPath());
            ByteArrayOutputStream stream = new ByteArrayOutputStream();
            bitmap.compress(Bitmap.CompressFormat.JPEG,100,stream);

            byte[] array = stream.toByteArray();
            encoded_string = Base64.encodeToString(array,0);

            return null;
        }

        @Override
        protected void onPostExecute(Void aVoid) {
            makeRequest();
        }

        private void makeRequest(){
            RequestQueue requestQueue = Volley.newRequestQueue(getApplicationContext());
            StringRequest request = new StringRequest(Request.Method.POST, getLocUrl(server),
                    new Response.Listener<String>() {
                        @Override
                        public void onResponse(String response) {

                        }
                    }, new Response.ErrorListener(){
                            @Override
                            public void onErrorResponse(VolleyError error){

                            }
                    }) {
                        @Override
                        protected Map<String,String> getParams() throws AuthFailureError{
                            HashMap<String,String> map = new HashMap<>();
                            map.put("encoded_string",encoded_string);
                            map.put("image_name",image_name);

                            return map;
                        }
                    };
            requestQueue.add(request);
        }
    }

//    public class GenericFileProvider extends FileProvider {
//
//    }

    /**
     * Gets the longitude and latitude of the android device and updates the url with them as parameters
     * @param url The original url to the server
     * @return The updated url with the location parameters
     */
    private String getLocUrl(String url) {

        try {
            LocationManager lm = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
            Location location = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER);

            //Get the latitude and longitude of the phone
            double lng = location.getLongitude();
            double lat = location.getLatitude();

            //Set them as parameters by appending them to the url
            return url + "?lat=" + String.valueOf(lat) + "&long=" + String.valueOf(lng);
        } catch (SecurityException e) {
            //If the user denies the app's access to the location, do nothing to the url
            return url;
        } catch (NullPointerException e) {
            return url + "?";
        }

    }



    public class JSONTask extends AsyncTask<String, String, String> {

        @Override
        protected String doInBackground(String... params) {
            HttpURLConnection con = null;
            BufferedReader reader = null;

            //The string in which the url is going to be set to
            String urlWithParams = getLocUrl(params[0]);

            try {
                URL url = new URL(urlWithParams);
                con = (HttpURLConnection) url.openConnection();
                con.setRequestMethod("GET");

                InputStream stream = con.getInputStream();

                reader = new BufferedReader(new InputStreamReader(stream));

                StringBuffer buffer = new StringBuffer();

                String line = "";
                while ((line = reader.readLine()) != null) {
                    buffer.append(line);
                }
                return buffer.toString();

            } catch (MalformedURLException e) {
//                e.printStackTrace();
            } catch (IOException e) {
//                e.printStackTrace();
            } finally {
                if (con != null) {
                    con.disconnect();
                }
                try {
                    if (reader != null) {
                        reader.close();
                    }
                } catch (IOException e) {
//                    e.printStackTrace();
                }
            }

            return null;
        }

        @Override
        protected void onPostExecute(String result) {
            super.onPostExecute(result);
            try {
                String[] r = result.split(",");
                p.setText(r[0].replace("\"", ""));
                lastUpdate.setText(r[1].replace("\"", ""));
            } catch (NullPointerException e) {
                //e.printStackTrace();
                p.setText("Bad");
                lastUpdate.setText("Connection");
            }

        }
    }

    public class ImageTask extends AsyncTask<String, String, Bitmap> {

        @Override
        protected Bitmap doInBackground(String... params) {
            HttpURLConnection con = null;

            //The string in which the url is going to be set to
            String urlWithParams = getLocUrl(params[0]) + "&image=True";

            try {
                URL url = new URL(urlWithParams);
                con = (HttpURLConnection) url.openConnection();
                con.setRequestMethod("GET");

                InputStream stream = con.getInputStream();

                return BitmapFactory.decodeStream(stream);

            } catch (MalformedURLException e) {
                //e.printStackTrace();
            } catch (IOException e) {
                //e.printStackTrace();
            } finally {
                if (con != null) {
                    con.disconnect();
                }
            }

            return null;
        }

        @Override
        protected void onPostExecute(Bitmap result) {
            super.onPostExecute(result);
            if (result == null) {
                Drawable noconnection = getResources().getDrawable( R.drawable.noconnection );
                graph.setImageDrawable(noconnection);
            } else {
                graph.setImageBitmap(result);
            }


        }
    }
}