# -*- mode: ruby -*-
# vi: set ft=ruby :

unless Vagrant.has_plugin?("vagrant-vbguest")
  system("vagrant plugin install vagrant-vbguest")
  puts "Dependencies installed, please try the command again."
  exit
end

Vagrant.configure("2") do |config|
	config.vm.box = "debian/jessie64"

    config.vm.provider :virtualbox do |v|
        v.memory = 4096
        v.customize ["modifyvm", :id, "--ioapic", "on"]
        v.cpus = 2
        v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
        v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
    end
	
	config.vm.network "forwarded_port", guest: 8000, host: 8000, auto_correct: true
    config.vm.network "forwarded_port", guest: 9200, host: 9200, auto_correct: true
    config.vm.network "forwarded_port", guest: 5432, host: 5432, auto_correct: true
    config.vm.network "forwarded_port", guest: 5601, host: 5601, auto_correct: true

	config.vm.provision :shell, :path => "install_vagrant.sh", :args => "django-dynamic-references", :binary => true
	config.vm.synced_folder ".", "/home/vagrant/django-dynamic-references", type: "virtualbox"

end
