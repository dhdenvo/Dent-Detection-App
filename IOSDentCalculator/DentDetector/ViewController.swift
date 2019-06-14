//
//  ViewController.swift
//  LineCalculator
//
//  Created by Derek Roy on 2019-05-21.
//  Copyright © 2019 IBM. All rights reserved.
//

import UIKit

class ViewController: UIViewController, UIImagePickerControllerDelegate,UINavigationControllerDelegate, URLSessionDelegate, URLSessionTaskDelegate, URLSessionDataDelegate{
    
    @IBOutlet weak var Camera: UIButton!
    @IBOutlet weak var Picture: UIImageView!
    @IBOutlet weak var People: UILabel!
    @IBOutlet weak var Last: UILabel!
    let url:String = "http://drv-ctp6.canlab.ibm.com:5000/dent"
    
    var timer = Timer()

    override func viewDidLoad() {
        super.viewDidLoad()
        
        let value = UIInterfaceOrientation.portrait.rawValue
        UIDevice.current.setValue(value, forKey: "orientation")
        UINavigationController.attemptRotationToDeviceOrientation()
    }
    
    @IBAction func CameraButton(_ sender: UIButton) {
        let image = UIImagePickerController()
        image.delegate = self
        image.sourceType = UIImagePickerController.SourceType.camera
        image.allowsEditing = false
        self.present(image, animated:true){
            //Complete
        }
    }
    
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
        if let image = info[UIImagePickerController.InfoKey.originalImage] as? UIImage{
//            Picture.image = image
            uploadImage(image:image)
            setValues()
        }
        self.dismiss(animated: true, completion: nil)
    }
    
    func uploadImage(image:UIImage){
        
        let imageData:Data = image.jpegData(compressionQuality: 1.0)!
        let filename = "line.png"

        // generate boundary string using a unique per-app string
        let boundary = UUID().uuidString

        let fieldName = "reqtype"
        let fieldValue = "fileupload"

        let fieldName2 = "userhash"
        let fieldValue2 = "caa3dce4fcb36cfdf9258ad9c"

        let config = URLSessionConfiguration.default
        let session = URLSession(configuration: config)

        // Set the URLRequest to POST and to the specified URL
        var urlRequest = URLRequest(url: URL(string: self.url)!)
        urlRequest.httpMethod = "POST"

        // Set Content-Type Header to multipart/form-data, this is equivalent to submitting form data with file upload in a web browser
        // And the boundary is also set here
        urlRequest.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var data = Data()

        // Add the reqtype field and its value to the raw http request data
        data.append("\r\n--\(boundary)\r\n".data(using: .utf8)!)
        data.append("Content-Disposition: form-data; name=\"\(fieldName)\"\r\n\r\n".data(using: .utf8)!)
        data.append("\(fieldValue)".data(using: .utf8)!)

        // Add the userhash field and its value to the raw http reqyest data
        data.append("\r\n--\(boundary)\r\n".data(using: .utf8)!)
        data.append("Content-Disposition: form-data; name=\"\(fieldName2)\"\r\n\r\n".data(using: .utf8)!)
        data.append("\(fieldValue2)".data(using: .utf8)!)

        // Add the image data to the raw http request data
        data.append("\r\n--\(boundary)\r\n".data(using: .utf8)!)
        data.append("Content-Disposition: form-data; name=\"fileToUpload\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        data.append("Content-Type: String\r\n\r\n".data(using: .utf8)!)
        data.append(imageData)

        // End the raw http request data, note that there is 2 extra dash ("-") at the end, this is to indicate the end of the data
        // According to the HTTP 1.1 specification https://tools.ietf.org/html/rfc7230
        data.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)

        // Send a POST request to the URL, with the data we created earlier
        session.uploadTask(with: urlRequest, from: data, completionHandler: { responseData, response, error in

            if(error != nil){
                print("\(error!.localizedDescription)")
            }

            guard let responseData = responseData else {
                print("no response data")
                return
            }

            if let responseString = String(data: responseData, encoding: .utf8) {
                var vals = responseString.split{$0 == ","}
                print("uploaded to: \(vals[2])  \(vals[3])")
                
                DispatchQueue.main.async{
                    self.People.text = String(vals[3])
                    let time = String(vals[2])
                    var start = Int(String(time.split{$0 == ":"}[0])) ?? 0
                    let end = String(time.split{$0 == ":"}[1])
                    
                    
                    if(start >= 12){
                        if(start == 12){
                            self.Last.text = "12:\(end) PM"
                        }
                        else{
                            start = start - 12
                            self.Last.text = "\(start):\(end) PM"
                        }
                    }
                    else{
                        self.Last.text = "\(start):\(end) AM"
                    }
                }
            }
        }).resume()
        
    }
    
    @objc func setValues(){
        let task = URLSession.shared.dataTask(with: URL(string: self.url)!) {(data, response, error) in
            guard let data = data else { return }
            let x = String(data: data, encoding: .utf8)!
            self.process(s:x)
        }
        task.resume()
    }
    
    func process(s:String){
        var out = s.split(separator: ",")
        
        DispatchQueue.main.async{
            self.People.text = String(out[0].dropFirst(1))
            self.Last.text = String(out[1].dropLast(2))
        }
    }
    
    @objc func setValues2(){
        let task = URLSession.shared.dataTask(with: URL(string: self.url+"&image=True")!) {(data, response, error) in
            guard let data = data else { return }
//            let x = String(data: data, encoding: .utf8)!
            self.process2(s:data)
        }
        task.resume()
    }
    
    func process2(s:Data){
        DispatchQueue.main.async{
            self.Picture.image = UIImage(data: s)
        }
    }
}
